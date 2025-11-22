from rest_framework import serializers
from .models import ( RobotTelemetry, ArmEndpose, JointVelocity, JointEffort, JointPosition, ArmStatus, JointStatus, FailedScheduledModel,
                        BatteryStatus, MapManagement, JointHeat
                    )

class RobotTelemetryLastSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotTelemetry
        fields = ['latest_room_reached','latest_bed_reached']

class RobotTelemetryLastMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotTelemetry
        fields = ['robot_map_file','robot_map_url']
    
class RobotTelemetryLastStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotTelemetry
        fields = ['status']

class RobotTelemetryLastVolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotTelemetry
        fields = ['volume']

class RobotTelemetryLastRobotEmergencySerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotTelemetry
        fields = ['robot_emergency']

class RobotTelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotTelemetry
        fields = "__all__"

class ArmEndposeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArmEndpose
        fields = "__all__"

class JointVelocitySerializer(serializers.ModelSerializer):
    class Meta:
        model = JointVelocity
        fields = "__all__"

class JointEffortSerializer(serializers.ModelSerializer):
    class Meta:
        model = JointEffort
        fields = "__all__"

class JointPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JointPosition
        fields = "__all__"

class ArmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArmStatus
        fields = "__all__"

class JointStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JointStatus
        fields = "__all__"

class FailedScheduledModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailedScheduledModel
        fields = "__all__"

class RobotTelemetryLastRobotRoomOpeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotTelemetry
        fields = ['robot_door_opening', 'robot_door_closing', 'latest_room_reached']

class BatteryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryStatus
        fields = "__all__"

class MapManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapManagement
        fields = "__all__"

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image_file and hasattr(obj.image_file, 'url'):
            file_url = obj.image_file.url
            return request.build_absolute_uri(file_url) if request else file_url
        return obj.image_url
    
class JointHeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = JointHeat
        fields = "__all__"