import os
import time
from django.db import models
from django.conf import settings
from mainapp.models import Patient

def image_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = int(time.time())
    patient_id = instance.patient.id if instance.patient else "unknown"
    return f"bp2_images/screenshot/patient_{patient_id}_{timestamp}{ext}"

def camera_image_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = int(time.time())
    patient_id = instance.patient.id if instance.patient else "unknown"
    return f"bp2_images/camera/patient_{patient_id}_{timestamp}{ext}"


class Bp2CheckMeModel(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='bp2_check_me_patient'
    )

    sys = models.CharField(max_length=20, null=True, blank=True)
    dia = models.CharField(max_length=20, null=True, blank=True)
    map = models.CharField(max_length=20, null=True, blank=True)
    pulse_rate_note = models.CharField(max_length=20, null=True, blank=True)

    image_url = models.URLField(max_length=500, blank=True, null=True)
    image_file = models.FileField(upload_to=image_upload_to, blank=True, null=True)

    camera_image_url = models.URLField(max_length=500, blank=True, null=True)
    camera_image_file = models.FileField(upload_to=camera_image_upload_to, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    data_time = models.TimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='vitals_management_created_by',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='vitals_management_updated_by',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.patient} is {self.is_active}"