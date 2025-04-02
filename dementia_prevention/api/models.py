from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='patient_profile'  # Changed from 'patient'
    )
    
    def __str__(self):
        return f"{self.user.username} (Patient)"

class Caregiver(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='caregiver_profile'  # Changed from 'caregiver'
    )
    qualifications = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    patients = models.ManyToManyField(Patient, related_name='caregivers', blank=True)
    
    def __str__(self):
        return f"{self.user.username} (Caregiver)"

class LifestyleData(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='lifestyle_entries'  # Changed from 'lifestyle_data'
    )
    physical_activity = models.IntegerField(default=0)
    healthy_diet = models.IntegerField(default=0)
    social_engagement = models.IntegerField(default=0)
    good_sleep = models.IntegerField(default=0)
    smoking = models.IntegerField(default=0)
    alcohol = models.IntegerField(default=0)
    stress = models.IntegerField(default=1)
    notes = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Lifestyle data for {self.user.username} on {self.date}"

class PendingVerification(models.Model):
    caregiver = models.ForeignKey(Caregiver, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('caregiver', 'patient')
    
    def __str__(self):
        return f"Verification for {self.patient} by {self.caregiver}"

class CognitiveTestQuestion(models.Model):
    QUESTION_TYPES = [
        ('memory', 'Memory'),
        ('calculation', 'Calculation'),
        ('language', 'Language'),
        ('orientation', 'Orientation'),
    ]
    
    question = models.TextField()
    options = models.JSONField(default=list)  # For multiple choice questions
    correct_answer = models.CharField(max_length=255)
    question_type = models.CharField(max_length=50, null=True, blank=True)
    difficulty = models.IntegerField(default=1)  # 1-5 scale
    
    def __str__(self):
        return f"{self.question_type} question: {self.question[:50]}..."

class CognitiveTestResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='cognitive_tests')
    score = models.FloatField()  # Score out of 10
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    details = models.JSONField()  # Stores the questions and answers
    date_taken = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient}: {self.score}/10 on {self.date_taken.strftime('%Y-%m-%d')}"

class BrainHealthAssessment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='assessments')
    score = models.FloatField()  # Overall brain health score (0-100)
    cognitive_score = models.FloatField()  # Cognitive test score (0-10)
    lifestyle_data = models.ForeignKey(LifestyleData, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Brain health assessment for {self.patient}: {self.score}/100"

class Recommendation(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    CATEGORY_CHOICES = [
        ('cognitive', 'Cognitive'),
        ('physical', 'Physical Activity'),
        ('nutrition', 'Nutrition'),
        ('sleep', 'Sleep'),
        ('stress', 'Stress Management'),
        ('social', 'Social Engagement'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='recommendations')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} for {self.patient}"