# from django.contrib import admin
# from .models import *

# admin.site.register(RobotTelemetry)
# admin.site.register(ArmEndpose)
# admin.site.register(JointVelocity)
# admin.site.register(JointEffort)
# admin.site.register(JointPosition)

from django.contrib import admin
from .models import (
    RobotTelemetry,
    ArmEndpose,
    JointVelocity,
    JointEffort,
    JointPosition,
    ArmStatus,
    JointStatus,
    FailedScheduledModel,
    MapManagement,
)

admin.site.register(MapManagement)

@admin.register(FailedScheduledModel)
class FailedScheduledAdmin(admin.ModelAdmin):
    list_display = (
        "room_name",
        "bed_name",
        "reason",
        "responded",
        "created_at",
        "updated_at",
    )
    search_fields = ("room_name", "bed_name", "reason")
    list_filter = ("responded", "created_at", "updated_at")

@admin.register(RobotTelemetry)
class RobotTelemetryAdmin(admin.ModelAdmin):
    list_display = (
        "robot_name",
        "robot_battery",
        "robot_break",
        "robot_emergency",
        "robot_in_dock",
        "status",
        "updated_at",
    )
    search_fields = ("robot_name",)
    list_filter = ("status", "robot_in_dock", "robot_break", "robot_emergency")


@admin.register(ArmEndpose)
class ArmEndposeAdmin(admin.ModelAdmin):
    list_display = ("x", "y", "z", "rx", "ry", "rz", "updated_at")


@admin.register(JointVelocity)
class JointVelocityAdmin(admin.ModelAdmin):
    list_display = ("j1", "j2", "j3", "j4", "j5", "j6", "updated_at")


@admin.register(JointEffort)
class JointEffortAdmin(admin.ModelAdmin):
    list_display = ("j1", "j2", "j3", "j4", "j5", "j6", "updated_at")


@admin.register(JointPosition)
class JointPositionAdmin(admin.ModelAdmin):
    list_display = ("j1", "j2", "j3", "j4", "j5", "j6", "updated_at")


@admin.register(ArmStatus)
class ArmStatusAdmin(admin.ModelAdmin):
    list_display = (
        "arm_number",
        "ctrl_mode",
        "arm_status",
        "mode_feed",
        "teach_mode",
        "motion_status",
        "trajectory_num",
        "created_at",
    )
    search_fields = ("arm_number", "arm_status")
    list_filter = ("ctrl_mode", "motion_status")


@admin.register(JointStatus)
class JointStatusAdmin(admin.ModelAdmin):
    list_display = ("joint_number", "limit", "comms", "motor", "created_at")
    list_filter = ("limit", "comms", "motor")
    search_fields = ("joint_number",)