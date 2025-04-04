from django.urls import path
from .views import check_auth
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    signup,
    login_view,
    user_dashboard,
    caregiver_dashboard,
    cognitive_test_questions,
    submit_cognitive_test,
    cognitive_test_history,
    lifestyle_data,
    lifestyle_stats,
    brain_health_history,
    recommendations,
    send_verification,
    verify_patient,
    caregiver_patients,
    add_patient,
    remove_patient
)

urlpatterns = [
    # Authentication
    path('signup/', signup, name='signup'),
    path('login_view/', login_view, name='login'),
    # Dashboard
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('caregiver-dashboard/', caregiver_dashboard, name='caregiver_dashboard'),
    
    # Cognitive Tests
    path('cognitive-tests-questions/', cognitive_test_questions, name='cognitive_test_questions'),
    path('cognitive-tests/submit/', submit_cognitive_test, name='submit_cognitive_test'),
    path('cognitive-tests/history/', cognitive_test_history, name='cognitive_test_history'),
    
    # Lifestyle Tracking
    path('lifestyle-data/', lifestyle_data, name='lifestyle_data'),
    path('lifestyle-stats/', lifestyle_stats, name='lifestyle_stats'),
    
    # Brain Health
    path('brain-health/', brain_health_history, name='brain_health_history'),
    
    # Recommendations
    path('recommendations/', recommendations, name='recommendations_list'),
    path('recommendations/<int:pk>/', recommendations, name='recommendation_detail'),
    
    # Caregiver-Patient Management
    path('send-verification/', send_verification, name='send_verification'),
    path('verify-patient/', verify_patient, name='verify_patient'),
    path('caregiver-patients/', caregiver_patients, name='caregiver_patients'),
    path('add-patient/', add_patient, name='add_patient'),
    path('remove-patient/<int:patient_id>/', remove_patient, name='remove_patient'),
    
    # Auth token (optional)
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('check-auth/', check_auth, name='check-auth'),
]