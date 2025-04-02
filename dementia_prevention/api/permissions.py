# permissions.py
from rest_framework.permissions import BasePermission

class IsCaregiver(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'caregiver')

class IsPatientCaregiver(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.caregivers.filter(id=request.user.caregiver.id).exists()
    