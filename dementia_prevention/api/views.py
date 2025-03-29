from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
from .models import CognitiveTestQuestion
import json

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        user = User(username=username, email=email, password=password)
        user.save()
        return JsonResponse({'message': 'Sign up successful'}, status=201)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username, password=password)
            return JsonResponse({'message': 'Login successful'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def cognitive_test_questions(request):
    if request.method == 'GET':
        questions = CognitiveTestQuestion.objects.all()
        question_list = []
        for question in questions:
            question_list.append({
                'id' : question.id,
                'question' : question.question,
                'options' : question.options,
            })
        return JsonResponse({'questions' : question_list}, status=200)
    return JsonResponse({'error' : 'Invalid request'}, status=400)

@csrf_exempt
def evaluate_cognitive_test(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_answers = data.get('answers') # expecting a list of {question_id, answer}

        score = 0
        for answer in user_answers:
            question = CognitiveTestQuestion.objects.get(id=answer['question_id'])
            if answer['answer'] == question.correct_answer:
                score += 1
        
        return JsonResponse({'score':score, 'total_question': len(user_answers)}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)
