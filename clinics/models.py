from accounts.models import Doctor, Patient
from django.db import models


class Clinic(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    doctor = models.ForeignKey(Doctor , on_delete=models.CASCADE, related_name='doctor')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,  related_name='patient')

    def __str__(self):
        return self.name
