from rest_framework import serializers
from .models import (
    User,
    Patient,
    Caregiver,
    CognitiveTestQuestion,
    CognitiveTestResult,
    LifestyleData,
    BrainHealthAssessment,
    Recommendation
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PatientDataSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Patient
        fields = '__all__'

class CaregiverSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Caregiver
        fields = '__all__'

class CognitiveTestQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CognitiveTestQuestion
        fields = '__all__'

class CognitiveTestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CognitiveTestResult
        fields = '__all__'

class LifestyleDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifestyleData
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class BrainHealthAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrainHealthAssessment
        fields = '__all__'

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'