from rest_framework import serializers
from .models import Bp2CheckMeModel


class Bp2CheckMeSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)  # assuming Patient has a "name"
    image_url = serializers.SerializerMethodField(read_only=True)  # auto-generate from file if present
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = Bp2CheckMeModel
        fields = [
            'id',
            'patient',
            'patient_name',
            'sys',
            'dia',
            'map',
            'pulse_rate_note',
            'image_file',
            'image_url',
            'is_active',
            'data_time',
            'created_at',
            'created_by',
            'created_by_username',
            'updated_at',
            'updated_by',
            'updated_by_username',
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image_file and hasattr(obj.image_file, 'url'):
            file_url = obj.image_file.url
            return request.build_absolute_uri(file_url) if request else file_url
        return obj.image_url
    # def get_image_url(self, obj):
    #     if obj.image_file:
    #         # force a consistent host, e.g., your server IP or domain
    #         return f"http://192.168.1.33:8000{obj.image_file.url}"
    #     return None



# # serializers.py
# from rest_framework import serializers
# from .models import Bp2CheckMeModel


# class Bp2CheckMeSerializer(serializers.ModelSerializer):
#     patient_name = serializers.CharField(source='patient.name', read_only=True)
#     created_by_username = serializers.CharField(source='created_by.username', read_only=True)
#     updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)

#     class Meta:
#         model = Bp2CheckMeModel
#         fields = [
#             'id',
#             'patient',
#             'patient_name',
#             'sys',
#             'dia',
#             'map',
#             'pulse_rate_note',
#             'is_active',
#             'data_read_time',
#             'created_at',
#             'created_by',
#             'created_by_username',
#             'updated_at',
#             'updated_by',
#             'updated_by_username',
#         ]
