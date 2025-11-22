from django.contrib import admin
from .models import *

admin.site.register(HealthcareUser)
admin.site.register(Patient)
admin.site.register(LocalIpModel)
admin.site.register(AlertHistory)