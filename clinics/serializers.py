from rest_framework import serializers, status

from .models import Clinic
from accounts.models import Doctor, Patient


class ClinicDoctorsSerializer(serializers.ModelSerializer):
    """ a serial class for clinic doctors api """
    patient= serializers.StringRelatedField()
    class Meta:
        model = Clinic
        fields = ('id','name', 'patient', 'date','start_time','end_time','price')
        read_only_fields =('id',)
    



class ClinicPatientSerializer(serializers.ModelSerializer):
    """ a serial class for clinic doctors api """
    class Meta:
        model = Clinic
        fields = ('id','name', 'doctor', 'date','start_time','end_time','price')
        read_only_fields =('id',)
    
  
    




    
