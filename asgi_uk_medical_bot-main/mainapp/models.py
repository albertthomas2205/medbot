from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings
from bed_data.models import SlotDataModel

class HealthcareUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('nurse', 'Nurse'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=False, blank=False) 
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, null=False, blank=False)
    gender = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # is active is in abstract user
    # username is in abstract user

    REQUIRED_FIELDS = ['name', 'role', 'email']

    def __str__(self):
        return f"{self.name} - {self.email} - {self.role}"

class Patient(models.Model):
    patient_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    slot_assigned = models.OneToOneField(
        SlotDataModel,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='slot_assigned',
        unique=True
    )

    gender = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='patients_created',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='patients_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.name} - is active {self.is_active}"

class LocalIpModel(models.Model):
    local_ip_add = models.CharField(max_length=100, unique=True)
    port = models.PositiveIntegerField(max_length=4, unique=True, null=True, blank=True)

    def __str__(self):
        return f"IP: {self.local_ip_add} / POST: {self.port}"
    
class AlertHistory(models.Model):
    room = models.CharField(max_length=100)
    bed = models.CharField(max_length=100)
    reason = models.TextField(max_length=100, null=True, blank=True)
    responded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    is_timed_out = models.BooleanField(default=False)
    is_help = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    not_me = models.BooleanField(default=False)
    is_patient_pop = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert in {self.room} {self.bed} responded = {self.responded}"