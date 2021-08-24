from django.contrib import admin
from .models import Clinic

class ClinicAdmin(admin.ModelAdmin):
   
    list_display = ('id', 'name', 'doctor','patient', 'date', 'start_time', 'end_time')
    list_display_links = ('id', 'name')
    list_filter = ('doctor','date',)
    search_fields = ('name', 'doctor__user__name', 'patient__user__name',)             
    list_per_page = 25

admin.site.register(Clinic , ClinicAdmin)
