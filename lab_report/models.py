from django.db import models

# Create your models here.
from django.db import models

class LabReport(models.Model):
    # Patient Information
    patient_name = models.CharField(max_length=100, blank=True, null=True)
    father_husband_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    nic_number = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    
    # Registration Information
    registration_date = models.DateTimeField(auto_now_add=True)
    registration_center = models.CharField(max_length=255, blank=True, null=True)
    specimen = models.CharField(max_length=255, blank=True, null=True)
    consultant_name = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    test_results = models.JSONField(default=dict, blank=True , null=True)