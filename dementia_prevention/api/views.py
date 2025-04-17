from django.http import JsonResponse
import logging
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.conf import settings
from datetime import datetime, timedelta
import json
import random
from django.db.models import Avg, Max, Min
from .models import (
    Patient, 
    Caregiver, 
    PendingVerification,
    CognitiveTestQuestion,
    CognitiveTestResult,
    LifestyleData,
    BrainHealthAssessment,
    Recommendation
)
from .serializers import (
    UserSerializer,
    PatientDataSerializer,
    CaregiverSerializer,
    LifestyleDataSerializer,
    CognitiveTestQuestionSerializer,
    CognitiveTestResultSerializer,
    BrainHealthAssessmentSerializer,
    RecommendationSerializer
)
from .utils import calculate_brain_health_score, generate_recommendations

logger = logging.getLogger(__name__)

@api_view(['GET'])
def check_session(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                # Add other user fields as needed
            }
        })
    return JsonResponse({'authenticated': False})
# Helper functions
def calculate_brain_health_score(cognitive_score, lifestyle_data):
    """
    Calculate a comprehensive brain health score based on cognitive test results and lifestyle factors
    """
    # Base score from cognitive test (0-100 scale)
    base_score = cognitive_score * 10  # Assuming cognitive_score is 0-10
    
    # Lifestyle adjustments
    lifestyle_score = 0
    
    # Positive lifestyle factors
    if lifestyle_data.get('physical_activity', 0) >= 3:  # 3+ times per week
        lifestyle_score += 15
    if lifestyle_data.get('healthy_diet', 0) >= 4:  # 4+ healthy meals per week
        lifestyle_score += 15
    if lifestyle_data.get('social_engagement', 0) >= 2:  # 2+ social activities per week
        lifestyle_score += 10
    if lifestyle_data.get('good_sleep', 0) >= 5:  # 5+ nights of good sleep per week
        lifestyle_score += 10
    
    # Negative lifestyle factors
    if lifestyle_data.get('smoking', 0) > 0:
        lifestyle_score -= 20
    if lifestyle_data.get('alcohol', 0) > 7:  # More than 7 drinks per week
        lifestyle_score -= 15
    if lifestyle_data.get('stress', 0) >= 4:  # High stress level (4 or 5 on 1-5 scale)
        lifestyle_score -= 10
    
    # Calculate final score (0-100 scale)
    final_score = min(max(base_score + lifestyle_score, 0), 100)
    
    return final_score

def generate_recommendations(brain_health_score, lifestyle_data):
    """
    Generate personalized recommendations based on brain health score and lifestyle data
    """
    recommendations = []
    
    # Cognitive recommendations
    if brain_health_score < 70:
        recommendations.append({
            'category': 'cognitive',
            'title': 'Brain Training Exercises',
            'description': 'Engage in daily brain training activities to improve cognitive function.',
            'priority': 'high'
        })
    
    # Physical activity recommendations
    if lifestyle_data.get('physical_activity', 0) < 3:
        recommendations.append({
            'category': 'physical',
            'title': 'Increase Physical Activity',
            'description': 'Aim for at least 30 minutes of moderate exercise 3-5 times per week.',
            'priority': 'medium'
        })
    
    # Diet recommendations
    if lifestyle_data.get('healthy_diet', 0) < 4:
        recommendations.append({
            'category': 'nutrition',
            'title': 'Improve Your Diet',
            'description': 'Incorporate more fruits, vegetables, and omega-3 rich foods into your meals.',
            'priority': 'medium'
        })
    
    # Sleep recommendations
    if lifestyle_data.get('good_sleep', 0) < 5:
        recommendations.append({
            'category': 'sleep',
            'title': 'Improve Sleep Quality',
            'description': 'Aim for 7-9 hours of quality sleep each night. Establish a regular sleep schedule.',
            'priority': 'high'
        })
    
    # Stress management recommendations
    if lifestyle_data.get('stress', 0) >= 3:
        recommendations.append({
            'category': 'stress',
            'title': 'Reduce Stress',
            'description': 'Practice mindfulness or meditation for 10-15 minutes daily to reduce stress.',
            'priority': 'high'
        })
    
    # Social engagement recommendations
    if lifestyle_data.get('social_engagement', 0) < 2:
        recommendations.append({
            'category': 'social',
            'title': 'Increase Social Engagement',
            'description': 'Participate in social activities at least twice a week to maintain cognitive health.',
            'priority': 'medium'
        })
    
    return recommendations

from rest_framework.permissions import AllowAny
@api_view(['POST', 'GET'])
@csrf_exempt
@permission_classes([AllowAny])
def signup_view(request):

    data = request.data
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Validate required fields
    missing_fields = []
    if not username:
        missing_fields.append('username')
    if not password:
        missing_fields.append('password')
    if not email:
        missing_fields.append('email')

    if missing_fields:
        return Response(
            {'detail': f"Missing required field(s): {', '.join(missing_fields)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if username or email already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'detail': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create the user
    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        
        # Log the user in (optional)
        login(request, user)
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Signup successful'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST', 'GET'])
def login_view(request):
    # Get username and password from request data
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'detail': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)

    # Check if authentication failed
    if not user:
        return Response(
            {'detail': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Login the user (creates session)
    login(request, user)

    
    return Response({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
    })

@api_view(['GET'])
def check_auth(request):
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username
            },
            'is_caregiver': hasattr(request.user, 'caregiver'),
            'is_patient': hasattr(request.user, 'patient')
        })
    return Response({'authenticated': False})

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """Main dashboard for both patients and caregivers"""
    try:
        user = request.user
        response_data = {
            'user': UserSerializer(user).data,
            'is_caregiver': hasattr(user, 'caregiver'),
            'is_patient': hasattr(user, 'patient')
        }
        
        if hasattr(user, 'patient'):
            # Patient-specific data
            patient = user.patient
            response_data['patient_data'] = PatientDataSerializer(patient).data
            
            # Get latest cognitive test result
            latest_test = CognitiveTestResult.objects.filter(patient=patient).order_by('-date_taken').first()
            if latest_test:
                response_data['latest_cognitive_score'] = CognitiveTestResultSerializer(latest_test).data
            
            # Get latest lifestyle data
            latest_lifestyle = LifestyleData.objects.filter(user=user).order_by('-date').first()
            if latest_lifestyle:
                response_data['latest_lifestyle_data'] = LifestyleDataSerializer(latest_lifestyle).data
            
            # Get latest brain health assessment
            latest_assessment = BrainHealthAssessment.objects.filter(patient=patient).order_by('-date').first()
            if latest_assessment:
                response_data['latest_assessment'] = BrainHealthAssessmentSerializer(latest_assessment).data
            
            # Get recommendations
            recommendations = Recommendation.objects.filter(patient=patient, completed=False)
            response_data['recommendations'] = RecommendationSerializer(recommendations, many=True).data
            
        elif hasattr(user, 'caregiver'):
            # Caregiver-specific data
            caregiver = user.caregiver
            response_data['caregiver_data'] = CaregiverSerializer(caregiver).data
            
            # Get connected patients
            patients = caregiver.patients.all()
            response_data['patients'] = PatientDataSerializer(patients, many=True).data
            
        return Response(response_data)
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def caregiver_dashboard(request):
    """Detailed dashboard for caregivers showing their patients' data"""
    try:
        if not hasattr(request.user, 'caregiver'):
            return Response(
                {'error': 'User is not a caregiver'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        caregiver = request.user.caregiver
        patients = caregiver.patients.all()
        
        patient_data = []
        for patient in patients:
            # Get patient's latest cognitive test
            latest_test = CognitiveTestResult.objects.filter(patient=patient).order_by('-date_taken').first()
            cognitive_data = CognitiveTestResultSerializer(latest_test).data if latest_test else None
            
            # Get patient's latest lifestyle data
            latest_lifestyle = LifestyleData.objects.filter(user=patient.user).order_by('-date').first()
            lifestyle_data = LifestyleDataSerializer(latest_lifestyle).data if latest_lifestyle else None
            
            # Get patient's latest assessment
            latest_assessment = BrainHealthAssessment.objects.filter(patient=patient).order_by('-date').first()
            assessment_data = BrainHealthAssessmentSerializer(latest_assessment).data if latest_assessment else None
            
            # Get patient's active recommendations
            recommendations = Recommendation.objects.filter(patient=patient, completed=False)
            recommendation_data = RecommendationSerializer(recommendations, many=True).data
            
            patient_data.append({
                'patient': PatientDataSerializer(patient).data,
                'cognitive_data': cognitive_data,
                'lifestyle_data': lifestyle_data,
                'assessment_data': assessment_data,
                'recommendations': recommendation_data
            })
        
        return Response({
            'caregiver': CaregiverSerializer(caregiver).data,
            'patients': patient_data
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
from functools import wraps
def json_login_required(view_func):
    """ Custom decorator to return JSON instead of redirecting """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized. Please log in.'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

ANSWER_KEY = {
    1: '12',
    2: 'July',
    3: 'Paris',
    4: '5',
    5: 'Mars',
    6: 'Blue Whale',
    7: '7',
    8: '8',
    9: 'Carbon Dioxide',
    10: 'William Shakespeare',
    
    # New 40 answers (questions 11-50)
    11: 'Joe Biden',
    12: '(Open-ended)',  # Personal memory
    13: 'Apple, Apricot, Avocado',
    14: '$30',
    15: '36',
    16: 'Thursday',
    17: 'Cold',
    18: 'Blue',
    19: 'DLROW',
    20: 'Carrot',
    21: '10',
    22: '6',
    23: 'George Washington',
    24: 'Atlantic',
    25: 'Blue',
    26: 'Square',
    27: 'Triangle',
    28: '(Assess response)',
    29: '(Assess sequencing)',
    30: '(Open-ended)',
    31: '(Open-ended)',
    32: '93',
    33: 'They weigh the same',
    34: '(Open-ended)',
    35: 'Pen',
    36: 'Yellow',
    37: '7',
    38: '9',
    39: 'Pencil',
    40: '(Assess recall)',
    41: '3:00',
    42: 'December',
    43: '(Open-ended)',
    44: '(Assess response)',
    45: 'Scissors',
    46: '4',
    47: '(Open-ended)',
    48: 'Night',
    49: 'Octagon',
    50: 'Shoes'
}

# Public-facing questions (answers stripped out)
QUESTIONS = [
    {
        'id': 1,
        'question': 'What is 5 + 7?',
        'options': ['10', '11', '12', '13']
    },
    {
        'id': 2,
        'question': 'Which month comes after June?',
        'options': ['May', 'July', 'August', 'September']
    },
    {
        'id': 3,
        'question': 'What is the capital of France?',
        'options': ['Berlin', 'Madrid', 'Paris', 'Rome']
    },
    {
        'id': 4,
        'question': 'What is 15 ÷ 3?',
        'options': ['3', '4', '5', '6']
    },
    {
        'id': 5,
        'question': 'Which planet is known as the Red Planet?',
        'options': ['Earth', 'Mars', 'Jupiter', 'Venus']
    },
    {
        'id': 6,
        'question': 'What is the largest mammal?',
        'options': ['Elephant', 'Blue Whale', 'Giraffe', 'Hippopotamus']
    },
    {
        'id': 7,
        'question': 'How many continents are there on Earth?',
        'options': ['5', '6', '7', '8']
    },
    {
        'id': 8,
        'question': 'What is the square root of 64?',
        'options': ['6', '7', '8', '9']
    },
    {
        'id': 9,
        'question': 'Which gas do plants use for photosynthesis?',
        'options': ['Oxygen', 'Carbon Dioxide', 'Nitrogen', 'Hydrogen']
    },
    {
        'id': 10,
        'question': 'Who wrote "Romeo and Juliet"?',
        'options': ['Charles Dickens', 'William Shakespeare', 'Mark Twain', 'Jane Austen']
    },

    # New 40 questions (id 11-50)
    {
        'id': 11,
        'question': 'What is the name of the current U.S. president?',
        'options': ['Joe Biden', 'Donald Trump', 'Barack Obama', 'George Bush']
    },
    {
        'id': 12,
        'question': 'What was the last holiday you celebrated?',
        'options': ['Christmas', 'Thanksgiving', 'Easter', 'New Year\'s']
    },
    {
        'id': 13,
        'question': 'Name three fruits that start with "A".',
        'options': ['Apple, Apricot, Avocado', 'Banana, Blueberry, Blackberry', 'Cherry, Coconut, Cantaloupe', 'Grape, Guava, Gooseberry']
    },
    {
        'id': 14,
        'question': 'If you buy an item for \$20 and pay with \$50, how much change do you get?',
        'options': ['\$20', '\$25', '\$30', '\$35']
    },
    {
        'id': 15,
        'question': 'What is 12 × 3?',
        'options': ['24', '36', '48', '60']
    },
    {
        'id': 16,
        'question': 'If today is Monday, what day is it in three days?',
        'options': ['Tuesday', 'Wednesday', 'Thursday', 'Friday']
    },
    {
        'id': 17,
        'question': 'What is the opposite of "hot"?',
        'options': ['Warm', 'Cold', 'Wet', 'Dry']
    },
    {
        'id': 18,
        'question': 'Complete this sentence: "The sky is ___."',
        'options': ['Green', 'Blue', 'Red', 'Black']
    },
    {
        'id': 19,
        'question': 'Spell "WORLD" backward.',
        'options': ['DLROW', 'DROWL', 'DLORW', 'DRLOW']
    },
    {
        'id': 20,
        'question': 'Which does not belong: Apple, Banana, Carrot, Orange?',
        'options': ['Apple', 'Banana', 'Carrot', 'Orange']
    },
    {
        'id': 21,
        'question': 'What comes next: 2, 4, 6, 8, ___?',
        'options': ['9', '10', '12', '14']
    },
    {
        'id': 22,
        'question': 'How many quarters make \$1.50?',
        'options': ['3', '4', '5', '6']
    },
    {
        'id': 23,
        'question': 'Who was the first U.S. president?',
        'options': ['Thomas Jefferson', 'George Washington', 'Abraham Lincoln', 'John Adams']
    },
    {
        'id': 24,
        'question': 'Which ocean is between the U.S. and Europe?',
        'options': ['Pacific', 'Indian', 'Atlantic', 'Arctic']
    },
    {
        'id': 25,
        'question': 'What is the main color of the U.S. flag?',
        'options': ['Red', 'Blue', 'Green', 'White']
    },
    {
        'id': 26,
        'question': 'Which shape has four equal sides?',
        'options': ['Triangle', 'Circle', 'Square', 'Rectangle']
    },
    {
        'id': 27,
        'question': 'Which of these is a triangle? (○, △, □, ☆)',
        'options': ['○', '△', '□', '☆']
    },
    {
        'id': 28,
        'question': 'Tap the table when I say "A": B, C, A, D, A, F.',
        'options': ['(Assess response)']
    },
    {
        'id': 29,
        'question': 'Name the months of the year in order.',
        'options': ['(Assess sequencing)']
    },
    {
        'id': 30,
        'question': 'What is your birth date?',
        'options': ['(Open-ended)']
    },
    {
        'id': 31,
        'question': 'Where were you born?',
        'options': ['(Open-ended)']
    },
    {
        'id': 32,
        'question': 'What is 100 minus 7?',
        'options': ['93', '83', '73', '63']
    },
    {
        'id': 33,
        'question': 'Which is heavier: a pound of feathers or a pound of bricks?',
        'options': ['Feathers', 'Bricks', 'They weigh the same', 'Depends']
    },
    {
        'id': 34,
        'question': 'What is the capital of your country?',
        'options': ['(Open-ended)']
    },
    {
        'id': 35,
        'question': 'What do you use to write on paper?',
        'options': ['Spoon', 'Pen', 'Hammer', 'Leaf']
    },
    {
        'id': 36,
        'question': 'What is the color of a ripe banana?',
        'options': ['Red', 'Blue', 'Yellow', 'Green']
    },
    {
        'id': 37,
        'question': 'How many days are in a week?',
        'options': ['5', '6', '7', '8']
    },
    {
        'id': 38,
        'question': 'What is the largest number: 5, 3, 9, 2?',
        'options': ['5', '3', '9', '2']
    },
    {
        'id': 39,
        'question': 'What is the name of this object? (Show a pencil)',
        'options': ['🖊️', '✏️', '📏', '🩹']
    },
    {
        'id': 40,
        'question': 'Repeat these words: "Cat, Ball, Shoe."',
        'options': ['(Assess recall)']
    },
    {
        'id': 41,
        'question': 'What time is it when the big hand is on 12 and the small hand is on 3?',
        'options': ['12:00', '3:00', '6:00', '9:00']
    },
    {
        'id': 42,
        'question': 'Which is not a season: Winter, Summer, December, Spring?',
        'options': ['Winter', 'Summer', 'December', 'Spring']
    },
    {
        'id': 43,
        'question': 'What is the name of the current year?',
        'options': ['(Open-ended)']
    },
    {
        'id': 44,
        'question': 'Point to the ceiling.',
        'options': ['(Assess response)']
    },
    {
        'id': 45,
        'question': 'What do you call the thing you use to cut paper?',
        'options': ['Spoon', 'Scissors', 'Plate', 'Sock']
    },
    {
        'id': 46,
        'question': 'How many legs does a chair usually have?',
        'options': ['1', '2', '3', '4']
    },
    {
        'id': 47,
        'question': 'What is the name of your spouse/partner?',
        'options': ['(Open-ended)']
    },
    {
        'id': 48,
        'question': 'What is the opposite of "day"?',
        'options': ['Night', 'Morning', 'Evening', 'Noon']
    },
    {
        'id': 49,
        'question': 'What is the shape of a stop sign?',
        'options': ['Circle', 'Square', 'Octagon', 'Triangle']
    },
    {
        'id': 50,
        'question': 'What do you wear on your feet?',
        'options': ['Hat', 'Shoes', 'Gloves', 'Scarf']
    }
]

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cognitive_test_questions(request):
    return JsonResponse({'questions': QUESTIONS})


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def submit_cognitive_test(request):
    try:
        data = request.data
        answers = data.get('answers', [])

        if not answers:
            return Response({'error': 'No answers provided'}, status=status.HTTP_400_BAD_REQUEST)

        total_questions = len(answers)
        correct_answers = 0

        for item in answers:
            q_id = item.get('question_id')
            user_answer = item.get('answer')
            correct_answer = ANSWER_KEY.get(q_id)
            if correct_answer and user_answer == correct_answer:
                correct_answers += 1

        score = round((correct_answers / total_questions) * 50, 1)

        if request.user.is_authenticated and hasattr(request.user, 'patient'):
            patient = request.user.patient

            test_result = CognitiveTestResult.objects.create(
                patient=patient,
                score=score,
                total_questions=total_questions,
                correct_answers=correct_answers,
                details=answers
            )

            latest_lifestyle = LifestyleData.objects.filter(user=request.user).order_by('-date').first()

            if latest_lifestyle:
                lifestyle_data = {
                    'physical_activity': latest_lifestyle.physical_activity,
                    'healthy_diet': latest_lifestyle.healthy_diet,
                    'social_engagement': latest_lifestyle.social_engagement,
                    'good_sleep': latest_lifestyle.good_sleep,
                    'smoking': latest_lifestyle.smoking,
                    'alcohol': latest_lifestyle.alcohol,
                    'stress': latest_lifestyle.stress
                }

                brain_health_score = calculate_brain_health_score(score, lifestyle_data)

                assessment, created = BrainHealthAssessment.objects.update_or_create(
                    patient=patient,
                    defaults={
                        'score': brain_health_score,
                        'cognitive_score': score,
                        'lifestyle_data': latest_lifestyle,
                        'date': datetime.now().date()
                    }
                )

                recommendations = generate_recommendations(brain_health_score, lifestyle_data)

                for rec in recommendations:
                    Recommendation.objects.create(
                        patient=patient,
                        category=rec['category'],
                        title=rec['title'],
                        description=rec['description'],
                        priority=rec['priority']
                    )

                return Response({
                    'test_result': CognitiveTestResultSerializer(test_result).data,
                    'brain_health_assessment': BrainHealthAssessmentSerializer(assessment).data,
                    'recommendations': recommendations,
                    'score': score
                })

            return Response({
                'test_result': CognitiveTestResultSerializer(test_result).data,
                'score': score
            })

        return Response({
            'score': score,
            'message': 'Results not saved as you are not a registered patient'
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cognitive_test_history(request):
    """Get a patient's cognitive test history"""
    try:
        if not hasattr(request.user, 'patient'):
            return Response(
                {'error': 'Only patients have cognitive test history'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        patient = request.user.patient
        tests = CognitiveTestResult.objects.filter(patient=patient).order_by('-date_taken')
        serializer = CognitiveTestResultSerializer(tests, many=True)
        
        # Calculate stats
        if tests.exists():
            stats = {
                'average_score': tests.aggregate(Avg('score'))['score__avg'],
                'highest_score': tests.aggregate(Max('score'))['score__max'],
                'lowest_score': tests.aggregate(Min('score'))['score__min'],
                'total_tests': tests.count()
            }
        else:
            stats = {}
        
        return Response({
            'tests': serializer.data,
            'stats': stats
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def lifestyle_data(request):
    """
    Handle lifestyle data submission and retrieval
    - GET: Returns all lifestyle entries for the authenticated user
    - POST: Creates a new lifestyle entry for the authenticated user
    """
    try:
        if request.method == 'GET':
            entries = LifestyleData.objects.filter(user=request.user).order_by('-date')
            serializer = LifestyleDataSerializer(entries, many=True)
            return Response({
                'count': entries.count(),
                'results': serializer.data
            })
        
        elif request.method == 'POST':
            # Ensure we don't have duplicate entries for the same date
            date = request.data.get('date', datetime.now().date())
            if LifestyleData.objects.filter(user=request.user, date=date).exists():
                return Response(
                    {'error': 'Lifestyle data already exists for this date'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = LifestyleDataSerializer(data=request.data)
            if serializer.is_valid():
                # Save with the authenticated user
                serializer.save(user=request.user)
                
                # If user is a patient, update brain health assessment
                if hasattr(request.user, 'patient'):
                    update_brain_health_assessment(request.user)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in lifestyle_data: {str(e)}")
        return Response(
            {'error': 'An error occurred while processing your request'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def update_brain_health_assessment(user):
    """Helper function to update brain health assessment after lifestyle data changes"""
    try:
        patient = user.patient
        latest_test = CognitiveTestResult.objects.filter(patient=patient).order_by('-date_taken').first()
        latest_lifestyle = LifestyleData.objects.filter(user=user).order_by('-date').first()

        if latest_test and latest_lifestyle:
            lifestyle_data = {
                'physical_activity': latest_lifestyle.physical_activity,
                'healthy_diet': latest_lifestyle.healthy_diet,
                'social_engagement': latest_lifestyle.social_engagement,
                'good_sleep': latest_lifestyle.good_sleep,
                'smoking': latest_lifestyle.smoking,
                'alcohol': latest_lifestyle.alcohol,
                'stress': latest_lifestyle.stress
            }
            
            brain_health_score = calculate_brain_health_score(latest_test.score, lifestyle_data)
            
            assessment, created = BrainHealthAssessment.objects.update_or_create(
                patient=patient,
                defaults={
                    'score': brain_health_score,
                    'cognitive_score': latest_test.score,
                    'lifestyle_data': latest_lifestyle,
                    'date': datetime.now().date()
                }
            )
            
            # Generate new recommendations
            Recommendation.objects.filter(patient=patient, completed=False).delete()
            recommendations = generate_recommendations(brain_health_score, lifestyle_data)
            
            for rec in recommendations:
                Recommendation.objects.create(
                    patient=patient,
                    category=rec['category'],
                    title=rec['title'],
                    description=rec['description'],
                    priority=rec['priority']
                )
            
            return assessment
    except Exception as e:
        logger.error(f"Error updating brain health assessment: {str(e)}")
        return None

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lifestyle_stats(request):
    """
    Get aggregated lifestyle statistics for the authenticated user
    - Returns averages and totals for different time periods
    """
    try:
        # Get time period filter (default: 30 days)
        time_period = request.GET.get('period', '30d')
        
        if time_period == '7d':
            date_filter = datetime.now() - timedelta(days=7)
        elif time_period == '30d':
            date_filter = datetime.now() - timedelta(days=30)
        elif time_period == '90d':
            date_filter = datetime.now() - timedelta(days=90)
        else:  # All time
            date_filter = None

        # Base queryset
        queryset = LifestyleData.objects.filter(user=request.user)
        if date_filter:
            queryset = queryset.filter(date__gte=date_filter)

        if not queryset.exists():
            return Response({'message': 'No lifestyle data available for the selected period'})

        # Calculate averages
        averages = queryset.aggregate(
            avg_physical_activity=Avg('physical_activity'),
            avg_healthy_diet=Avg('healthy_diet'),
            avg_social_engagement=Avg('social_engagement'),
            avg_good_sleep=Avg('good_sleep'),
            avg_stress=Avg('stress'),
            avg_smoking=Avg('smoking'),
            avg_alcohol=Avg('alcohol')
        )

        # Calculate totals where applicable
        totals = queryset.aggregate(
            total_physical_activity=Sum('physical_activity'),
            total_healthy_meals=Sum('healthy_diet')
        )

        # Get latest entry
        latest_entry = LifestyleDataSerializer(
            queryset.order_by('-date').first()
        ).data

        return Response({
            'period': time_period,
            'averages': averages,
            'totals': totals,
            'latest_entry': latest_entry,
            'entry_count': queryset.count()
        })

    except Exception as e:
        logger.error(f"Error in lifestyle_stats: {str(e)}")
        return Response(
            {'error': 'An error occurred while processing your request'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lifestyle_trends(request):
    """
    Get lifestyle data trends over time for charting
    - Returns data grouped by week/month
    """
    try:
        # Get grouping parameter (default: week)
        group_by = request.GET.get('group_by', 'week')
        
        queryset = LifestyleData.objects.filter(user=request.user)
        
        if not queryset.exists():
            return Response({'message': 'No lifestyle data available'})

        # Annotate with time period
        if group_by == 'month':
            queryset = queryset.extra(
                select={'period': "DATE_FORMAT(date, '%%Y-%%m')"}
            ).values('period').annotate(
                physical_activity=Avg('physical_activity'),
                healthy_diet=Avg('healthy_diet'),
                social_engagement=Avg('social_engagement'),
                good_sleep=Avg('good_sleep'),
                stress=Avg('stress')
            ).order_by('period')
        else:  # week
            queryset = queryset.extra(
                select={'period': "CONCAT(YEAR(date), '-', WEEK(date))"}
            ).values('period').annotate(
                physical_activity=Avg('physical_activity'),
                healthy_diet=Avg('healthy_diet'),
                social_engagement=Avg('social_engagement'),
                good_sleep=Avg('good_sleep'),
                stress=Avg('stress')
            ).order_by('period')

        return Response(list(queryset))

    except Exception as e:
        logger.error(f"Error in lifestyle_trends: {str(e)}")
        return Response(
            {'error': 'An error occurred while processing your request'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Brain Health Assessment Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brain_health_history(request):
    """Get brain health assessment history"""
    try:
        if not hasattr(request.user, 'patient'):
            return Response(
                {'error': 'Only patients have brain health assessments'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        patient = request.user.patient
        assessments = BrainHealthAssessment.objects.filter(patient=patient).order_by('-date')
        serializer = BrainHealthAssessmentSerializer(assessments, many=True)
        
        # Calculate stats
        if assessments.exists():
            stats = {
                'average_score': assessments.aggregate(Avg('score'))['score__avg'],
                'highest_score': assessments.aggregate(Max('score'))['score__max'],
                'lowest_score': assessments.aggregate(Min('score'))['score__min'],
                'total_assessments': assessments.count()
            }
        else:
            stats = {}
        
        return Response({
            'assessments': serializer.data,
            'stats': stats
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Recommendation Views
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def recommendations(request, pk=None):
    """Get or update recommendations"""
    try:
        if not hasattr(request.user, 'patient'):
            return Response(
                {'error': 'Only patients have recommendations'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        patient = request.user.patient
        
        if request.method == 'GET':
            if pk:
                # Get single recommendation
                recommendation = Recommendation.objects.get(id=pk, patient=patient)
                serializer = RecommendationSerializer(recommendation)
            else:
                # Get all recommendations
                recommendations = Recommendation.objects.filter(patient=patient).order_by('-priority', '-date_created')
                serializer = RecommendationSerializer(recommendations, many=True)
            
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            # Mark recommendation as completed
            recommendation = Recommendation.objects.get(id=pk, patient=patient)
            recommendation.completed = request.data.get('completed', recommendation.completed)
            recommendation.save()
            
            return Response(RecommendationSerializer(recommendation).data)
    
    except Recommendation.DoesNotExist:
        return Response(
            {'error': 'Recommendation not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Caregiver-Patient Management Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_verification(request):
    """Send verification code to patient for caregiver connection"""
    try:
        if not hasattr(request.user, 'caregiver'):
            return Response(
                {'message': 'Only caregivers can send verification'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        caregiver = request.user.caregiver
        patient_email = request.data.get('patient_email')
        
        if not patient_email:
            return Response(
                {'message': 'Patient email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            patient = Patient.objects.get(user__email=patient_email)
        except Patient.DoesNotExist:
            return Response(
                {'message': 'Patient not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already connected
        if caregiver.patients.filter(id=patient.id).exists():
            return Response(
                {'message': 'Already connected to this patient'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate and store verification code
        code = str(random.randint(100000, 999999))
        PendingVerification.objects.update_or_create(
            caregiver=caregiver,
            patient=patient,
            defaults={'verification_code': code}
        )
        
        # Send email
        send_mail(
            'Caregiver Connection Request',
            f'Your verification code is: {code}\n\nShare this code with your caregiver to connect.',
            settings.DEFAULT_FROM_EMAIL,
            [patient_email],
            fail_silently=False,
        )
        
        return Response({'message': 'Verification code sent'})
    
    except Exception as e:
        return Response(
            {'message': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_patient(request):
    """Verify patient connection with verification code"""
    try:
        if not hasattr(request.user, 'caregiver'):
            return Response(
                {'message': 'Only caregivers can verify patients'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        caregiver = request.user.caregiver
        patient_email = request.data.get('patient_email')
        verification_code = request.data.get('verification_code')
        
        if not all([patient_email, verification_code]):
            return Response(
                {'message': 'Patient email and verification code are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verification = PendingVerification.objects.get(
                caregiver=caregiver,
                patient__user__email=patient_email,
                verification_code=verification_code
            )
            
            # Add relationship
            caregiver.patients.add(verification.patient)
            verification.delete()
            
            return Response({'message': 'Patient successfully added'})
            
        except PendingVerification.DoesNotExist:
            return Response(
                {'message': 'Invalid verification code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response(
            {'message': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def caregiver_patients(request):
    """Get list of patients connected to a caregiver"""
    try:
        if not hasattr(request.user, 'caregiver'):
            return Response(
                {'error': 'User is not a caregiver'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        caregiver = request.user.caregiver
        patients = caregiver.patients.all()
        serializer = PatientDataSerializer(patients, many=True)
        
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_patient(request):
    """Add a patient to caregiver's list (admin function)"""
    try:
        if not hasattr(request.user, 'caregiver'):
            return Response(
                {'error': 'User is not a caregiver'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        caregiver = request.user.caregiver
        patient_id = request.data.get('patient_id')
        
        if not patient_id:
            return Response(
                {'error': 'Patient ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            patient = Patient.objects.get(id=patient_id)
            
            # Check if already connected
            if caregiver.patients.filter(id=patient.id).exists():
                return Response(
                    {'message': 'Already connected to this patient'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            caregiver.patients.add(patient)
            return Response({'message': 'Patient added successfully'})
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Patient not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_patient(request, patient_id):
    """Remove a patient from caregiver's list"""
    try:
        if not hasattr(request.user, 'caregiver'):
            return Response(
                {'error': 'User is not a caregiver'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        caregiver = request.user.caregiver
        
        try:
            patient = Patient.objects.get(id=patient_id)
            caregiver.patients.remove(patient)
            return Response({'message': 'Patient removed successfully'})
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Patient not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
