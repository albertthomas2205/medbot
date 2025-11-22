import os
import time
from django.db import models
from django.conf import settings

def video_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = int(time.time())
    safe_name = instance.video_name.replace(" ", "_").lower()
    return f"demo_data/{safe_name}_{timestamp}{ext}"

class VideoManagementModel(models.Model):
    video_name = models.CharField(max_length=20)

    video_image_url = models.URLField(max_length=500, blank=True, null=True)
    video_image_file = models.FileField(upload_to=video_upload_to, blank=True, null=True)

    is_image = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='video_management_created_by',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='video_management_updated_by',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.video_name} is {self.is_active}"