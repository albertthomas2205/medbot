from rest_framework import serializers
from .models import PrivilegeModel

class PrivilegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivilegeModel
        fields = ['id', 'code', 'allow_admin', 'allow_nurse']