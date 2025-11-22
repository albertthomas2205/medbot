from django.db import models

# Create your models here.
from django.conf import settings

class PrivilegeModel(models.Model):
    code = models.CharField(max_length=100, unique=True)
    allow_admin = models.BooleanField(default=True)
    allow_nurse = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} - {self.allow_admin} - {self.allow_nurse}"
