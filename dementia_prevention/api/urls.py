from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('cognitive-test-questions/', views.cognitive_test_questions, name='cognitive_test_questions'),
    path('evaluate-cognitive-test/', views.evaluate_cognitive_test, name='evaluate_cognitive_test'),
]