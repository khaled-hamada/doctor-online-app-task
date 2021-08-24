from rest_framework import generics ,viewsets ,status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.response import Response

from .permissions import IsDoctor, IsPatient
from .serializers import ClinicDoctorsSerializer, ClinicPatientSerializer
from .models import Clinic
from accounts.models import Doctor, Patient

from datetime import datetime, date as cur_date
import datetime as dt

class DoctorClinic(generics.ListAPIView):
    serializer_class = ClinicDoctorsSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, IsDoctor,)
    
    queryset = Clinic.objects.all()

    def get_queryset(self):
        doctor = Doctor.objects.get(user = self.request.user)
        qs = self.queryset
        return qs.filter(doctor = doctor)


class PatientClinc(viewsets.ModelViewSet):
    serializer_class = ClinicPatientSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, IsPatient,)
    queryset = Clinic.objects.all()
    
    def get_queryset(self):
        patient = Patient.objects.get(user=self.request.user)
        qs = self.queryset
        return qs.filter(patient = patient)
    
    def __test_no_overlap(self, request, update_flag, **kwargs):
        """ helper function for both create and update to avoid code duplication
            and increase readability
            update_flag -> False create 
                        -> True update
        """
        data = request.data
        # filter query set depending on flag to avoid errors comparing the
        # same clinic reservation to itself in case of updating
        if update_flag:
          
            updated_clc = self.queryset.get(id = int(kwargs.get('pk')))
            qs = self.queryset.exclude(id = updated_clc.id)
        else: # create 
            qs = self.queryset

        if update_flag:
            doctor = data.get('doctor', updated_clc.doctor.id)
            if doctor:
                doctor = Doctor.objects.get(id=int(doctor))
            date = data.get('date', updated_clc.date)
            start_time = data.get('start_time', updated_clc.start_time)
            end_time = data.get('end_time', updated_clc.end_time)
           
        else:
            doctor = data.get('doctor', None)
            if doctor:
                doctor = Doctor.objects.get(id=int(doctor))
            date = data.get('date', cur_date.today())
            start_time = data.get('start_time', datetime.now().time())
            end_time = data.get('end_time', datetime.now().time())

        ## check start time is valid
        # start time overlaps if start_time_old <= start_time_new AND
        #                        end_time_old > start_time_new
        st_time_overlap = qs.filter(
            doctor=doctor, date=date,
            start_time__lte = start_time,
            end_time__gt = start_time).exists()
       
        if st_time_overlap:
            return False

        #check end_time
        # end time overlaps if start_time_old <= end_time_new AND
        #                        end_time_old > start_time_new
        end_time_overlap = qs.filter(
            doctor=doctor, date=date,
            start_time__lte=end_time,
            end_time__gt=end_time).exists()
       
        if end_time_overlap:
           return False

        #3. test end_time is greater than start time
        # make sure both start time and end time are of the same type 
        # not a datatime and a string 
        if not isinstance(start_time , datetime):
            # start time or end time is in the form H:M:S.ms 
            # i want to remove the fractional part (ms) to avoid conversion errors 
            # it is already a string object because it is not a datetime instance 
            # but to be very sure and avoid extra errors i convert it first to string 
            # then split and take the first part only which is H:M:S
            # or i can add .%f after %S ('%H:%M:%S.%f') but there is no need for these micro seconds

            start_time = str(start_time).split('.')[0] 
            start_time = datetime.strptime(start_time, '%H:%M:%S')
            
        if not isinstance(end_time, datetime):
            end_time = str(end_time).split('.')[0]
            end_time = datetime.strptime(end_time, '%H:%M:%S')

        if start_time > end_time:
            return False
        
        # success no overlap and end_time is greeater than start time at least by 1 second 
        return True
    
    def create(self, request, *args, **kwargs):
        """ override create method to check for valid time slots """
        if self.__test_no_overlap(request, False, **kwargs):
            data = request.data
            patient = Patient.objects.get(user=request.user)
            clc_ser = ClinicPatientSerializer(data = data)
        
            if clc_ser.is_valid():
                clc_ser.save(patient = patient)
               
                return Response(clc_ser.data, status=status.HTTP_201_CREATED)
            else :
                return Response(clc_ser.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
           return Response(data={}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def update(self, request, *args, **kwargs):
        """ override update function to avoid reservations overlapping """
        # check if to see first if request contains start or end time field 
       
        if self.__test_no_overlap(request, True, **kwargs):
            data = request.data
            patient = Patient.objects.get(user=request.user)
            clc = self.queryset.get(id = int( kwargs.get('pk')))
            
            # check first to see partial update (patch req) or full update (put req)
            partial = bool(kwargs.get('partial', False))
            clc_ser = ClinicPatientSerializer(clc, data=data, partial = partial)
            if clc_ser.is_valid():
                clc_ser.save(patient=patient)
                return Response(clc_ser.data, status=status.HTTP_200_OK)
            
            else:
                return Response(clc_ser.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={}, status=status.HTTP_400_BAD_REQUEST)
       
       
       
