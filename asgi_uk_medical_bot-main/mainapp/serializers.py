from rest_framework import serializers
from .models import HealthcareUser, Patient, LocalIpModel, AlertHistory
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from bed_data.models import SlotDataModel, RoomDataModel
from bed_data.serializer import SlotDataPatientListSerializer

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = HealthcareUser.objects.filter(username=username,is_active=True).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid username or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is deactivated")

        tokens = RefreshToken.for_user(user)
            
        # Update last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        response_data = {
            "user_id": user.pk,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "access_token": str(tokens.access_token),
            "refresh_token": str(tokens),
            "registered_date": user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return response_data

class HealthcareUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthcareUser
        fields = [
            'id',
            'username',
            'password',
            'name',
            'email',
            'role',
            'gender',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = HealthcareUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data['name'],
            email=validated_data['email'],
            gender=validated_data['gender'],
            role=validated_data['role'],
        )
        return user
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  # ✅ hashes password
        instance.save()
        return instance

class PatientSerializer(serializers.ModelSerializer):
    slot_assigned = SlotDataPatientListSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id',
            'patient_id',
            'name',
            'slot_assigned',
            'gender',
            'age',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

class PatientSlotAssignSerializer(serializers.ModelSerializer):
    slot_assigned = serializers.PrimaryKeyRelatedField(
        queryset=SlotDataModel.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Patient
        fields = ['patient_id', 'slot_assigned']
        extra_kwargs = {
            'patient_id': {'required': True},
        }

    def update(self, instance, validated_data):
        instance.slot_assigned = validated_data.get('slot_assigned', instance.slot_assigned)
        if 'updated_by' in self.context:
            instance.updated_by = self.context['updated_by']
        instance.save()
        return instance

class LocalIpSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalIpModel
        fields = '__all__'

class AlertHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertHistory
        fields = '__all__'
