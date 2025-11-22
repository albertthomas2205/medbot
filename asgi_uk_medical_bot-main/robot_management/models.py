from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class RobotTelemetry(models.Model):

    class BatchRefreshWeek(models.TextChoices):
        MONDAY = "monday", "Monday"
        TUESDAY = "tuesday", "Tuesday"
        WEDNESDAY = "wednesday", "Wednesday"
        THURSDAY = "thursday", "Thursday"
        FRIDAY = "friday", "Friday"
        SATURDAY = "saturday", "Saturday"
        SUNDAY = "sunday", "Sunday"
        
    robot_name = models.CharField(default="Med Bot")
    robot_battery = models.IntegerField(default=0)
    robot_break = models.BooleanField(default=False)
    robot_emergency = models.BooleanField(default=False)
    robot_physical_emergency = models.BooleanField(default=False)
    robot_in_dock = models.BooleanField(default=False)
    robot_is_charging = models.BooleanField(default=False)
    robot_power_stage = models.CharField(default=False)
    robot_sleep_mode = models.CharField(default=False)

    robot_image_file = models.FileField(upload_to="stcm_image", null=True, blank=True)

    robot_door_opening = models.BooleanField(default=False)
    robot_door_closing = models.BooleanField(default=False)

    latest_room_reached = models.CharField(null=True, blank=True)
    latest_bed_reached = models.CharField(null=True, blank=True)

    maintenance_start_date = models.DateField(null=True, blank=True)
    maintenance_end_date = models.DateField(null=True, blank=True)
    maintenance_limit = models.TimeField(null=True, blank=True)

    working_time = models.TimeField(null=True, blank=True)
    status = models.BooleanField(default=True)
    volume = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    batch_refresh_week = models.CharField(
        max_length=10,
        choices=BatchRefreshWeek.choices,
        default=BatchRefreshWeek.MONDAY,
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RobotTelemetry singleton"
    
class ArmEndpose(models.Model):
    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)
    z = models.FloatField(default=0.0)
    rx = models.FloatField(default=0.0)
    ry = models.FloatField(default=0.0)
    rz = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Endpose (x={self.x}, y={self.y}, z={self.z}, rx={self.rx}, ry={self.ry}, rz={self.rz})"
    
class JointVelocity(models.Model):
    j1 = models.FloatField(default=0.0)
    j2 = models.FloatField(default=0.0)
    j3 = models.FloatField(default=0.0)
    j4 = models.FloatField(default=0.0)
    j5 = models.FloatField(default=0.0)
    j6 = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"JointVelocity(j1={self.j1}, j2={self.j2}, j3={self.j3}, j4={self.j4}, j5={self.j5}, j6={self.j6})"

class JointEffort(models.Model):
    j1 = models.FloatField(default=0.0)
    j2 = models.FloatField(default=0.0)
    j3 = models.FloatField(default=0.0)
    j4 = models.FloatField(default=0.0)
    j5 = models.FloatField(default=0.0)
    j6 = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"JointEffort(j1={self.j1}, j2={self.j2}, j3={self.j3}, j4={self.j4}, j5={self.j5}, j6={self.j6})"
    
class JointPosition(models.Model):
    j1 = models.FloatField(default=0.0)
    j2 = models.FloatField(default=0.0)
    j3 = models.FloatField(default=0.0)
    j4 = models.FloatField(default=0.0)
    j5 = models.FloatField(default=0.0)
    j6 = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"JointPosition(j1={self.j1}, j2={self.j2}, j3={self.j3}, j4={self.j4}, j5={self.j5}, j6={self.j6})"
    
class JointHeat(models.Model):
    j1 = models.FloatField(default=0.0)
    j2 = models.FloatField(default=0.0)
    j3 = models.FloatField(default=0.0)
    j4 = models.FloatField(default=0.0)
    j5 = models.FloatField(default=0.0)
    j6 = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"JointHeat(j1={self.j1}, j2={self.j2}, j3={self.j3}, j4={self.j4}, j5={self.j5}, j6={self.j6})"

class ArmStatus(models.Model):
    ctrl_mode = models.CharField(max_length=50, blank=True)
    ctrl_mode_timestamp = models.DateTimeField(null=True, blank=True)

    arm_status = models.CharField(max_length=50, blank=True)
    arm_status_timestamp = models.DateTimeField(null=True, blank=True)

    mode_feed = models.CharField(max_length=50, blank=True)
    mode_feed_timestamp = models.DateTimeField(null=True, blank=True)

    teach_mode = models.CharField(max_length=50, blank=True)
    teach_mode_timestamp = models.DateTimeField(null=True, blank=True)

    motion_status = models.CharField(max_length=50, blank=True)
    motion_status_timestamp = models.DateTimeField(null=True, blank=True)

    trajectory_num = models.CharField(max_length=20, blank=True)
    trajectory_num_timestamp = models.DateTimeField(null=True, blank=True)

    arm_number = models.IntegerField(default=1)

    voltage_too_low = models.CharField(max_length=50, blank=True)
    voltage_too_low_timestamp = models.DateTimeField(null=True, blank=True)

    motor_overheating = models.CharField(max_length=50, blank=True)
    motor_overheating_timestamp = models.DateTimeField(null=True, blank=True)

    driver_overcurrent = models.CharField(max_length=50, blank=True)
    driver_overcurrent_timestamp = models.DateTimeField(null=True, blank=True)

    driver_overheating = models.CharField(max_length=50, blank=True)
    driver_overheating_timestamp = models.DateTimeField(null=True, blank=True)

    sensor_status = models.CharField(max_length=50, blank=True)
    sensor_status_timestamp = models.DateTimeField(null=True, blank=True)

    driver_error_status = models.CharField(max_length=50, blank=True)
    driver_error_status_timestamp = models.DateTimeField(null=True, blank=True)

    driver_enable_status = models.CharField(max_length=50, blank=True)
    driver_enable_status_timestamp = models.DateTimeField(null=True, blank=True)

    homing_status = models.CharField(max_length=50, blank=True)
    homing_status_timestamp = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old = ArmStatus.objects.get(pk=self.pk)
            for field in [
                "ctrl_mode", "arm_status", "mode_feed", "teach_mode", "motion_status",
                "trajectory_num", "voltage_too_low", "motor_overheating", "driver_overcurrent",
                "driver_overheating", "sensor_status", "driver_error_status", "driver_enable_status",
                "homing_status"
            ]:
                if getattr(old, field) != getattr(self, field):
                    setattr(self, f"{field}_timestamp", timezone.now())
        else:
            # On create, initialize all timestamps
            for field in [
                "ctrl_mode", "arm_status", "mode_feed", "teach_mode", "motion_status",
                "trajectory_num", "voltage_too_low", "motor_overheating", "driver_overcurrent",
                "driver_overheating", "sensor_status", "driver_error_status", "driver_enable_status",
                "homing_status"
            ]:
                setattr(self, f"{field}_timestamp", timezone.now())

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Arm {self.arm_number} - {self.arm_status}"

class JointStatus(models.Model):
    JOINT_CHOICES = [(str(i), f"Joint {i}") for i in range(1, 6)]
    joint_number = models.CharField(max_length=1, choices=JOINT_CHOICES)

    limit = models.CharField(max_length=50, blank=True)
    limit_timestamp = models.DateTimeField(null=True, blank=True)

    comms = models.CharField(max_length=50, blank=True)
    comms_timestamp = models.DateTimeField(null=True, blank=True)

    motor = models.CharField(max_length=50, blank=True)
    motor_timestamp = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old = JointStatus.objects.get(pk=self.pk)
            for field in [
                "limit", "comms", "motor"
            ]:
                if getattr(old, field) != getattr(self, field):
                    setattr(self, f"{field}_timestamp", timezone.now())
        else:
            # On create, initialize all timestamps
            for field in [
                "limit", "comms", "motor"
            ]:
                setattr(self, f"{field}_timestamp", timezone.now())

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Arm {self.joint_number} - Joint {self.joint_number}"
    
class FailedScheduledModel(models.Model):
    room_name = models.CharField(max_length=255)
    bed_name = models.CharField(null=True, blank=True, max_length=255)
    reason = models.TextField(null=True, blank=True, max_length=255)
    responded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room_name}::{self.bed_name} is {self.responded}"
    
class BatteryStatus(models.Model):
    charge = models.CharField(default=0.0)
    voltage = models.CharField(default=0.0)
    current = models.CharField(default=0.0)
    power = models.CharField(default=0.0)
    temperature = models.CharField(default=0.0)
    time_left = models.CharField(default=0.0)
    count = models.CharField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.charge} - {self.voltage} - {self.current} - {self.power} - {self.temperature} - {self.time_left} - {self.count}"
    
class MapManagement(models.Model):
    map_name = models.CharField(max_length=255, unique=True)
    robot_map_file = models.FileField(null=True, blank=True, upload_to="robot_maps/")
    robot_map_url = models.URLField(null=True, blank=True)
    robot_map_image_file = models.FileField(null=True, blank=True, upload_to="robot_maps_image/")
    robot_map_image_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.map_name} ({'Active' if self.is_active else 'Inactive'}) - Created on {self.created_at.strftime('%Y-%m-%d')}"