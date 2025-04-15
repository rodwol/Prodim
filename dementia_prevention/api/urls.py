from django.urls import path
from .views import check_auth
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views
from .views import (
    signup_view,
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
    lifestyle_trends,
    verify_patient,
    caregiver_patients,
    add_patient,
    remove_patient
)

urlpatterns = [
    # Authentication
    path('signup_view/', signup_view, name='signup_view'),
    path('login_view/', login_view, name='login_view'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('caregiver-dashboard/', caregiver_dashboard, name='caregiver_dashboard'),
    
    # Cognitive Tests
    path('cognitive-tests-questions/', cognitive_test_questions, name='cognitive_test_questions'),
    path('submit_cognitive_test', submit_cognitive_test, name='submit_cognitive_test'),
    path('cognitive-tests/history/', cognitive_test_history, name='cognitive_test_history'),
    
    # Lifestyle Tracking
    path('lifestyle-data/', lifestyle_data, name='lifestyle_data'),
    path('lifestyle-stats/', lifestyle_stats, name='lifestyle_stats'),
    path('lifestyle-trends/', lifestyle_trends, name='lifestyle-trends'),
    
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