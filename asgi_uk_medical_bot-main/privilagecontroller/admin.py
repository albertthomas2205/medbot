from django.contrib import admin
from .models import PrivilegeModel
@admin.register(PrivilegeModel)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('code', 'allow_admin', 'allow_nurse')
    list_editable = ('allow_admin', 'allow_nurse')
    search_fields = ['code']
