from rest_framework import serializers
from .models import RoomDataModel, BedDataModel, SlotDataModel, RoomPositionModel
from mainapp.models import Patient

class RoomDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomDataModel
        fields = '__all__'

class BedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BedDataModel
        fields = '__all__'

class PatientRoomBedUpdateSerializer(serializers.ModelSerializer):
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=RoomDataModel.objects.all(),
        source='room',
        required=False,
        allow_null=True
    )
    bed_id = serializers.PrimaryKeyRelatedField(
        queryset=BedDataModel.objects.all(),
        source='bed',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Patient
        fields = ['room_id', 'bed_id']

class SlotDataModelSerializer(serializers.ModelSerializer):
    room_name = RoomDataSerializer(read_only=True)
    bed_name = BedDataSerializer(read_only=True)

    # Accept IDs for write operations
    room_name_id = serializers.PrimaryKeyRelatedField(
        source="room_name", queryset=RoomDataModel.objects.all(),
        write_only=True, required=False, allow_null=True
    )
    bed_name_id = serializers.PrimaryKeyRelatedField(
        source="bed_name", queryset=BedDataModel.objects.all(),
        write_only=True, required=False, allow_null=True
    )

    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SlotDataModel
        fields = [
            "id",
            "room_name",      # nested output
            "room_name_id",   # input
            "bed_name",       # nested output
            "bed_name_id",    # input
            "x",
            "y",
            "yaw",
            "is_active",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = ("created_at", "updated_at", "created_by", "updated_by")

class RoomPositionModelSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room_name.room_name', read_only=True)

    room_name_id = serializers.PrimaryKeyRelatedField(
        source="room_name", queryset=RoomDataModel.objects.all(),
        write_only=True, required=False, allow_null=True
    )

    entry_point = serializers.SerializerMethodField()
    exit_point = serializers.SerializerMethodField()

    class Meta:
        model = RoomPositionModel
        fields = [
            'id',
            'room_name',
            'room_name_id',
            'entry_point',
            'exit_point',
            'is_active',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

    def get_entry_point(self, obj):
        return {
            "x": obj.entry_point_x,
            "y": obj.entry_point_y,
            "yaw": obj.entry_point_yaw
        }

    def get_exit_point(self, obj):
        return {
            "x": obj.exit_point_x,
            "y": obj.exit_point_y,
            "yaw": obj.exit_point_yaw
        }

    def to_internal_value(self, data):
        """
        Flatten entry_point and exit_point dicts back into model fields
        when saving.
        """
        if "entry_point" in data:
            ep = data.get("entry_point") or {}
            data["entry_point_x"] = ep.get("x")
            data["entry_point_y"] = ep.get("y")
            data["entry_point_yaw"] = ep.get("yaw")

        if "exit_point" in data:
            xp = data.get("exit_point") or {}
            data["exit_point_x"] = xp.get("x")
            data["exit_point_y"] = xp.get("y")
            data["exit_point_yaw"] = xp.get("yaw")

        return super().to_internal_value(data)

class SlotDataPatientListSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room_name.room_name', read_only=True)
    bed_name = serializers.CharField(source='bed_name.bed_name', read_only=True)

    class Meta:
        model = SlotDataModel
        fields = ['room_name', 'bed_name']

class RoomCordSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoomPositionModel
        fields = '__all__'

class SlotCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlotDataModel
        fields = ['x', 'y', 'yaw']


class RoomPositionMiniSerializer(serializers.ModelSerializer):
    entry_point = serializers.SerializerMethodField()
    exit_point = serializers.SerializerMethodField()

    class Meta:
        model = RoomPositionModel
        fields = ["entry_point", "exit_point"]

    def get_entry_point(self, obj):
        return {
            "x": obj.entry_point_x,
            "y": obj.entry_point_y,
            "yaw": obj.entry_point_yaw,
        }

    def get_exit_point(self, obj):
        return {
            "x": obj.exit_point_x,
            "y": obj.exit_point_y,
            "yaw": obj.exit_point_yaw,
        }
