from accounts.models import Doctor, Patient
from  clinics.models import Clinic
from clinics.serializers import ClinicDoctorsSerializer, ClinicPatientSerializer

from decimal import *

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient
from datetime import date, datetime, timedelta

DOCTOR_CLINIC_URL = reverse('clinics:doctors')
PATIENT_CLINIC_URL = reverse('clinics:clinic-list')
CREATE_USER_URL = reverse('accounts:create')

def generate_detail_url(id):
    return reverse('clinics:clinic-detail', args=[id])

def create_test_user(**kwargs):
    return get_user_model().objects.create(**kwargs)
    
def create_test_doctor(**kwargs):
    payload= {
        'email': "doctor@gmail.com",
        'password': 'pass123456',
        'name': 'myname',
       
    }
    payload.update(**kwargs)
    user = create_test_user(**payload)
    doctor = Doctor.objects.create(user = user)
    return doctor, user

def create_test_patient(**kwargs):
    payload = {
        'email': "patient@gmail.com",
        'password': 'pass123456',
        'name': 'myname',
    }
    payload.update(**kwargs)
    user = create_test_user(**payload)

    patient = Patient.objects.create(user=user)
    return patient, user

def create_test_clinics(doctor , patient , **kwargs):
    payload = {
        'name':'doctor-patient',
        'price':150.4,
        'date':date.today(),
        'start_time': datetime.now().time(),
        "end_time": (datetime.now() + timedelta(hours=1)).time(),

    }
    payload.update(kwargs)
    clinic = Clinic.objects.create(doctor = doctor, patient = patient , **payload)
    return clinic
class PublicClinicApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user(
            email = "a@gmail.com",
            password='pass123456',
            name = 'myname',
           
        )

    def test_access_clinics_api_requires_authentication(self):
        """ test_access_clinics_api_requires_authentication """
        res = self.client.get(DOCTOR_CLINIC_URL)
        self.assertEqual(res.status_code , status.HTTP_401_UNAUTHORIZED)


class PrivateDoctorsClinicApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_only_doctors_can_access_doctor_api(self):
        """test_only_doctors_can_access_doctor_api """
        #create a patient account
        patient, user = create_test_patient()
        self.client.force_authenticate(user)
        res = self.client.get(DOCTOR_CLINIC_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        #create a  doctor account
        doctor, user = create_test_doctor()
        self.client.force_authenticate(user)
        res = self.client.get(DOCTOR_CLINIC_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrive_related_clinics_only(self):
        doctor, d_user = create_test_doctor(name="khaled")
        patient, _ = create_test_patient(name="osman")
        clc = create_test_clinics(doctor, patient, name="k-o-c")
        
        doctor_2, _ = create_test_doctor(email="docor_2@gmail.com")
        create_test_clinics(doctor_2, patient, name="k-o-c-2")

        self.client.force_authenticate(d_user)
        res = self.client.get(DOCTOR_CLINIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(Clinic.objects.all().count(), 2 )

        clc_ser = ClinicDoctorsSerializer(clc)
        self.assertIn(clc_ser.data , res.data)

       

class PrivatePatientClinicApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_only_pateint_can_access_patient_api(self):
        """test_only_doctors_can_access_doctor_api """
        #create a doctor account
        doctor, user = create_test_doctor()
        self.client.force_authenticate(user)
        res = self.client.get(PATIENT_CLINIC_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        #create a  patient account
        patient, user = create_test_patient()
        self.client.force_authenticate(user)
        res = self.client.get(PATIENT_CLINIC_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrive_related_clinics_only(self):
        doctor, _ = create_test_doctor(name="khaled")
        patient, p_user = create_test_patient(name="osman")
        clc = create_test_clinics(doctor, patient, name="k-o-c")
        
        patient_2, _ = create_test_patient(email="patient_2@gmail.com")
        create_test_clinics(doctor, patient_2, name="k-o-c-2")

        self.client.force_authenticate(p_user)
        res = self.client.get(PATIENT_CLINIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(Clinic.objects.all().count(), 2 )

        clc_ser = ClinicPatientSerializer(clc)
        self.assertIn(clc_ser.data , res.data)

    
    def test_create_valid_invalid_clinics(self):
        """ test creating both invalid and valid reservations  """
        doctor, _ = create_test_doctor(name="khaled")
        patient, p_user = create_test_patient(name="osman")
       
        payload = {
            'name': 'doctor-patient',
            'price': 150.4,
            'date': date.today(),
            'start_time': datetime.now().time(),
            "end_time": (datetime.now() + timedelta(hours=1)).time(),
            'doctor': doctor.id,

        }

        self.client.force_authenticate(p_user)
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(res.status_code , status.HTTP_201_CREATED)
    
        ## create wrong to test all edge cases 
        #1. start time over laps 
        payload['start_time'] = (datetime.now() + timedelta(minutes=58)).time()
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(res.status_code , status.HTTP_400_BAD_REQUEST)
        #assert not created i.e total clinics is 1 
        self.assertEqual(Clinic.objects.all().count(), 1)
        
        #2. end time over laps 
        payload['start_time'] = (datetime.now() + timedelta(minutes = -40)).time()
        payload['end_time'] = (datetime.now() + timedelta(minutes=59)).time()
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(res.status_code , status.HTTP_400_BAD_REQUEST)
        #assert not created i.e total clinics is 1 
        self.assertEqual(Clinic.objects.all().count(), 1)

        #3. both start and end time over laps 
        payload['start_time'] = (datetime.now() + timedelta(minutes = 4)).time()
        payload['end_time'] = (datetime.now() + timedelta(minutes=40)).time()
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(res.status_code , status.HTTP_400_BAD_REQUEST)
        #assert not created i.e total clinics is 1 
        self.assertEqual(Clinic.objects.all().count(), 1)
        
        #4. pass invalid data 
        payload.pop('start_time') 
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        #assert not created i.e total clinics is 1
        self.assertEqual(Clinic.objects.all().count(), 1)
        
        # create correct reservations 
        #5. create a new reservation with correct start and end time before the current one
        payload['start_time'] = (datetime.now() + timedelta(hours=-2)).time()
        payload['end_time'] = (datetime.now() + timedelta(hours=-1)).time()
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        #assert is created i.e total clinics is 2
        self.assertEqual(Clinic.objects.all().count(), 2)

        #6. create a new reservation with correct start and end time after the current two
        payload['start_time'] = (datetime.now() + timedelta(hours=1 )).time()
        payload['end_time'] = (datetime.now() + timedelta(hours=2)).time()
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        #assert is created i.e total clinics is 3
        self.assertEqual(Clinic.objects.all().count(), 3)

    
    def test_delete_clinics(self):
        doctor, _ = create_test_doctor(name="khaled")
        patient, p_user = create_test_patient(name="osman")
       
        payload = {
            'name': 'doctor-patient',
            'price': 150.4,
            'date': date.today(),
            'start_time': datetime.now().time(),
            "end_time": (datetime.now() + timedelta(hours=1)).time(),
            'doctor': doctor.id,

        }

        self.client.force_authenticate(p_user)
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        
        #2. 
        payload['start_time'] = (datetime.now() + timedelta(hours=1 )).time()
        payload['end_time'] = (datetime.now() + timedelta(hours=2)).time()
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        #assert is created i.e total clinics is 2
        self.assertEqual(Clinic.objects.all().count(), 2)

        #delete last one created
        clc = Clinic.objects.get(id = res.data['id'])
        res = self.client.delete(generate_detail_url(clc.id))
        self.assertEqual(res.status_code , status.HTTP_204_NO_CONTENT)
        #assert is deleted i.e total clinics is 1
        self.assertEqual(Clinic.objects.all().count(), 1)

    

    def test_update_clinics_success(self):
        """ test updating existing clinics reservations both valid and invalid """
        doctor, _ = create_test_doctor(name="khaled")
        patient, p_user = create_test_patient(name="osman")
       
        payload = {
            'name': 'doctor-patient',
            'price': 150.4,
            'date': date.today(),
            'start_time': datetime.now().time(),
            "end_time": (datetime.now() + timedelta(hours=1)).time(),
            'doctor': doctor.id,

        }

        self.client.force_authenticate(p_user)
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(res.status_code , status.HTTP_201_CREATED)
        clc = Clinic.objects.get(id = res.data['id'])
        
        #create another reservation
        payload['start_time'] = (datetime.now() + timedelta(hours=1)).time()
        payload['end_time'] = (datetime.now() + timedelta(hours=2)).time()
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(Clinic.objects.all().count(), 2)

        # test patch first
        # test update name
        res = self.client.patch(generate_detail_url(clc.id), {'name': 'name'})
        self.assertEqual(res.status_code , status.HTTP_200_OK)
        clc.refresh_from_db()
        self.assertEqual(clc.name , 'name')

        #test update start_time
        res = self.client.patch(
                            generate_detail_url(clc.id),
                            {'start_time': (datetime.now() + timedelta(minutes=30)).time()}
                            )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        clc.refresh_from_db()
        self.assertEqual(clc.name, 'name')

        # test update using put
        payload['name'] = "dummy name"
        payload['start_time'] = (datetime.now() + timedelta(minutes=30)).time()
        
        res = self.client.put(generate_detail_url(res.data['id']), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        clc.refresh_from_db()
        self.assertEqual(clc.name, 'dummy name')
        
    def test_update_clinics_failed(self):
        doctor, _ = create_test_doctor(name="khaled")
        patient, p_user = create_test_patient(name="osman")

        payload = {
            'name': 'doctor-patient',
            'price': 150.4,
            'date': date.today(),
            'start_time': datetime.now().time(),
            "end_time": (datetime.now() + timedelta(hours=1)).time(),
            'doctor': doctor.id,
        }

        self.client.force_authenticate(p_user)
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        #create another reservation
        payload['start_time'] = (datetime.now() + timedelta(hours=1)).time()
        payload['end_time'] = (datetime.now() + timedelta(hours=2)).time()
        res = self.client.post(PATIENT_CLINIC_URL, payload)
        self.assertEqual(Clinic.objects.all().count(), 2)

        clc = Clinic.objects.get(id = int(res.data['id']))
        #test update start_time fails due to overlapping 
        res = self.client.patch(
            generate_detail_url(clc.id),
            {'start_time': (datetime.now() + timedelta(minutes=30)).time()}
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        clc.refresh_from_db()

        #test update end_time fails due to overlapping 
        res = self.client.patch(
            generate_detail_url(clc.id),
            {'start_time': (datetime.now() + timedelta(minutes=-30)).time(),
            'end_time': (datetime.now() + timedelta(minutes=30)).time()}
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        clc.refresh_from_db()
       







