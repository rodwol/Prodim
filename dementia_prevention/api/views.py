from django.http import JsonResponse
import logging
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
import json
import random
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min

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
@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            user_type = data.get('user_type', 'patient')  # 'patient' or 'caregiver'

            if not all([username, email, password]):
                return JsonResponse(
                    {'error': 'All fields are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(username=username).exists():
                return JsonResponse(
                    {'error': 'Username already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if User.objects.filter(email=email).exists():
                return JsonResponse(
                    {'error': 'Email already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create patient or caregiver profile based on user type
            if user_type == 'caregiver':
                Caregiver.objects.create(user=user)
            else:
                Patient.objects.create(user=user)
            
            return JsonResponse(
                {'message': 'Sign up successful'}, 
                status=status.HTTP_201_CREATED
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid JSON'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return JsonResponse(
        {'error': 'Invalid request method'}, 
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@api_view(['POST'])
def login_view(request):
    # Get username and password from request data
    username = request.data.get('username')
    password = request.data.get('password')

    if request.method == 'GET':
        return Response(
            {"detail": "Use POST to authenticate"}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            headers={'Allow': 'POST'}
        )

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
    
    # Check user profiles
    try:
        is_caregiver = hasattr(user, 'caregiver')
        is_patient = hasattr(user, 'patient')
    except Exception as e:
        return Response(
            {'detail': 'Error checking user profile'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_caregiver': is_caregiver,
        'is_patient': is_patient
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
            'is_caregiver': hasattr(request.user, 'caregiver_profile'),
            'is_patient': hasattr(request.user, 'patient_profile')
        })
    return Response({'authenticated': False})

@api_view(['POST'])
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

@require_GET
@login_required
def cognitive_test_questions(request):
        questions = [
        {
            'id': 1,
            'question': 'What is 5 + 7?',
            'options': ['10', '11', '12', '13'],
            'answer': '12'
        },
        {
            'id': 2,
            'question': 'Which month comes after June?',
            'options': ['May', 'July', 'August', 'September'],
            'answer': 'July'
        },
        {
            'id': 3,
            'question': 'What is the capital of France?',
            'options': ['Berlin', 'Madrid', 'Paris', 'Rome'],
            'answer': 'Paris'
        },
        {
            'id': 4,
            'question': 'What is 15 ÷ 3?',
            'options': ['3', '4', '5', '6'],
            'answer': '5'
        },
        {
            'id': 5,
            'question': 'Which planet is known as the Red Planet?',
            'options': ['Earth', 'Mars', 'Jupiter', 'Venus'],
            'answer': 'Mars'
        },
        {
            'id': 6,
            'question': 'What is the largest mammal?',
            'options': ['Elephant', 'Blue Whale', 'Giraffe', 'Hippopotamus'],
            'answer': 'Blue Whale'
        },
        {
            'id': 7,
            'question': 'How many continents are there on Earth?',
            'options': ['5', '6', '7', '8'],
            'answer': '7'
        },
        {
            'id': 8,
            'question': 'What is the square root of 64?',
            'options': ['6', '7', '8', '9'],
            'answer': '8'
        },
        {
            'id': 9,
            'question': 'Which gas do plants use for photosynthesis?',
            'options': ['Oxygen', 'Carbon Dioxide', 'Nitrogen', 'Hydrogen'],
            'answer': 'Carbon Dioxide'
        },
        {
            'id': 10,
            'question': 'Who wrote "Romeo and Juliet"?',
            'options': ['Charles Dickens', 'William Shakespeare', 'Mark Twain', 'Jane Austen'],
            'answer': 'William Shakespeare'
        }
    ]
        return JsonResponse({'questions': questions})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_cognitive_test(request):
    """Submit cognitive test answers and get results"""
    try:
        if not hasattr(request.user, 'patient'):
            return Response(
                {'error': 'Only patients can take cognitive tests'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        patient = request.user.patient
        answers = request.data.get('answers', [])
        
        if not answers:
            return Response(
                {'error': 'No answers provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate score
        total_questions = len(answers)
        correct_answers = 0
        
        for answer in answers:
            question_id = answer.get('question_id')
            user_answer = answer.get('answer')
            
            try:
                question = CognitiveTestQuestion.objects.get(id=question_id)
                if user_answer == question.correct_answer:
                    correct_answers += 1
            except CognitiveTestQuestion.DoesNotExist:
                continue
        
        score = round((correct_answers / total_questions) * 10, 1)  # Score out of 10
        
        # Save test result
        test_result = CognitiveTestResult.objects.create(
            patient=patient,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            details=answers
        )
        
        # Check if we have lifestyle data to create a brain health assessment
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
            
            # Create or update brain health assessment
            assessment, created = BrainHealthAssessment.objects.update_or_create(
                patient=patient,
                defaults={
                    'score': brain_health_score,
                    'cognitive_score': score,
                    'lifestyle_data': latest_lifestyle,
                    'date': datetime.now().date()
                }
            )
            
            # Generate recommendations
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
                'recommendations': recommendations
            })
        
        return Response(CognitiveTestResultSerializer(test_result).data)
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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

# Lifestyle Tracking Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lifestyle_data(request):
    """Get or submit lifestyle data"""
    try:
        if request.method == 'GET':
            # Get all lifestyle entries for the user
            entries = LifestyleData.objects.filter(user=request.user).order_by('-date')
            serializer = LifestyleDataSerializer(entries, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Submit new lifestyle data
            serializer = LifestyleDataSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(user=request.user)
                
                # Check if we have cognitive data to create/update brain health assessment
                latest_test = CognitiveTestResult.objects.filter(patient__user=request.user).order_by('-date_taken').first()
                
                if latest_test and hasattr(request.user, 'patient'):
                    lifestyle_data = {
                        'physical_activity': serializer.validated_data.get('physical_activity', 0),
                        'healthy_diet': serializer.validated_data.get('healthy_diet', 0),
                        'social_engagement': serializer.validated_data.get('social_engagement', 0),
                        'good_sleep': serializer.validated_data.get('good_sleep', 0),
                        'smoking': serializer.validated_data.get('smoking', 0),
                        'alcohol': serializer.validated_data.get('alcohol', 0),
                        'stress': serializer.validated_data.get('stress', 0)
                    }
                    
                    brain_health_score = calculate_brain_health_score(latest_test.score, lifestyle_data)
                    
                    # Create or update brain health assessment
                    assessment, created = BrainHealthAssessment.objects.update_or_create(
                        patient=request.user.patient,
                        defaults={
                            'score': brain_health_score,
                            'cognitive_score': latest_test.score,
                            'lifestyle_data': serializer.instance,
                            'date': datetime.now().date()
                        }
                    )
                    
                    # Generate recommendations
                    recommendations = generate_recommendations(brain_health_score, lifestyle_data)
                    
                    for rec in recommendations:
                        Recommendation.objects.create(
                            patient=request.user.patient,
                            category=rec['category'],
                            title=rec['title'],
                            description=rec['description'],
                            priority=rec['priority']
                        )
                    
                    return Response({
                        'lifestyle_data': serializer.data,
                        'brain_health_assessment': BrainHealthAssessmentSerializer(assessment).data,
                        'recommendations': recommendations
                    }, status=status.HTTP_201_CREATED)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lifestyle_stats(request):
    """Get lifestyle statistics and trends"""
    try:
        # Get data for the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        entries = LifestyleData.objects.filter(
            user=request.user,
            date__gte=thirty_days_ago
        ).order_by('date')
        
        if not entries.exists():
            return Response({'message': 'No lifestyle data available'})
        
        serializer = LifestyleDataSerializer(entries, many=True)
        
        # Calculate averages
        averages = {
            'physical_activity': entries.aggregate(Avg('physical_activity'))['physical_activity__avg'],
            'healthy_diet': entries.aggregate(Avg('healthy_diet'))['healthy_diet__avg'],
            'social_engagement': entries.aggregate(Avg('social_engagement'))['social_engagement__avg'],
            'good_sleep': entries.aggregate(Avg('good_sleep'))['good_sleep__avg'],
            'stress': entries.aggregate(Avg('stress'))['stress__avg']
        }
        
        return Response({
            'entries': serializer.data,
            'averages': averages
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
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
