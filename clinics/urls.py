from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('patients', views.PatientClinc)

app_name = 'clinics'

urlpatterns = [
    path('doctors', views.DoctorClinic.as_view(), name='doctors'),
    path('', include(router.urls)),
]
