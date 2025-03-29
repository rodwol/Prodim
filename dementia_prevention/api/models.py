from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=100)
    family_history = models.BooleanField(default=False)
    genetic_predisposition = models.DateTimeField(auto_now_add=True)

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(Self):
        return self.username

class CognitiveTestQuestion(models.Model):
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=100)
    memory_score = models.FloatField()
    attention_score = models.FloatField()
    reasoning_score = models.FloatField()
    date_taken = models.DateTimeField(auto_now_add=True) """
    question = models.CharField(max_length=500)
    options = models.JSONField() # store options as a JSON array
    correct_answer = models.CharField(max_length=100)

    def __str__(self):
        return self.question

class RiskFactor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    smoking = models.BooleanField(default=False)
    alcohol_consumption = models.BooleanField(default=False)
    physical_activity = models.CharField(max_length=50)
    lifestyle_factors = models.TextField()
    sleep_quality = models.CharField(max_length=50)

class HealthDashboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    brain_health_score = models.FloatField()
    risk_areas = models.JSONField() # stores key risk areas as JSON
    prevention_strategies = models.TextField()

