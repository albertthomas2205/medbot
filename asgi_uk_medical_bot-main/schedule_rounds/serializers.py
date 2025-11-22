from rest_framework import serializers
from .models import BatchScheduleModel, ScheduledSlots, LogScheduler
from mainapp.models import Patient
from bed_data.serializer import SlotDataModelSerializer

class BatchScheduleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchScheduleModel
        fields = '__all__'

# serializers.py
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'  # add fields you want


class BatchScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchScheduleModel
        fields = '__all__'  # adjust as needed


class ScheduledSlotsSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    batch = BatchScheduleSerializer(read_only=True)
    bed_name = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledSlots
        fields = '__all__'

    def get_bed_name(self, obj):
        # Access the patient's assigned slot
        slot_obj = getattr(obj.patient, 'slot_assigned', None)
        if slot_obj and slot_obj.bed_name:
            return slot_obj.bed_name.bed_name
        return None

class ScheduledSlotsSchedulerSerializer(serializers.ModelSerializer):
    # patient = PatientSerializer(read_only=True)
    # batch = BatchScheduleSerializer(read_only=True)
    slot = SlotDataModelSerializer(source="patient.slot_assigned", read_only=True)
    # room_name = serializers.CharField(source='room_name.room_name', read_only=True)

    # room_position = RoomPositionMiniSerializer(
    #     source="slot.room_name.room_single_data",  # because of related_name in RoomPositionModel
    #     read_only=True
    # )

    class Meta:
        model = ScheduledSlots
        fields = '__all__'
        

class ScheduledSlotsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScheduledSlots
        fields = '__all__'

class LogSchedulerSerializer(serializers.ModelSerializer):

    class Meta:
        model = LogScheduler
        fields = '__all__'