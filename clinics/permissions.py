from accounts.models import Doctor, Patient
from rest_framework import permissions


class IsDoctor(permissions.BasePermission):
    """
     Custom permission to only allow doctors  to access doctors clinic api
    """

    def has_permission(self, request, view):
        """ check if request.user is instance of Doctor """
        doctor = Doctor.objects.filter(user = request.user).exists() # True of False
        return doctor

   

class IsPatient(permissions.BasePermission):
    """
     Custom permission to only allow patients  to access patient clinic api
    """

    def has_permission(self, request, view):
        """ check if request.user is instance of Doctor """
        patient = Patient.objects.filter(user=request.user).exists()  # True of False
        return patient
    
 