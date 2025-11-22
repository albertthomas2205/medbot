from django.db import models
from django.conf import settings
from mainapp.models import Patient
from bed_data.models import BedDataModel, RoomDataModel

class BatchScheduleModel(models.Model):
    TIME_SLOT_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ]

    batch_name = models.CharField(max_length=20, default="Default Batch")

    time_slot = models.CharField(
        max_length=20,
        choices=TIME_SLOT_CHOICES
    )

    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    trigger_time = models.TimeField(null=True, blank=True)

    is_stopped = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)
    completed_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='round_schedules_created',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='round_schedules_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        days = []
        if self.monday: days.append("Mon")
        if self.tuesday: days.append("Tue")
        if self.wednesday: days.append("Wed")
        if self.thursday: days.append("Thu")
        if self.friday: days.append("Fri")
        if self.saturday: days.append("Sat")
        if self.sunday: days.append("Sun")
        
        return f"{self.time_slot} - {self.trigger_time} on {', '.join(days)}"
    
class ScheduledSlots(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='scheduled_slots_patient',
        unique=True
    )

    batch = models.ForeignKey(
        BatchScheduleModel,
        on_delete=models.CASCADE,
        related_name='scheduled_slots_batches'
    )

    is_active = models.BooleanField(default=True)

    row_number = models.PositiveIntegerField(default=0)

    schedule_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='scheduled_slots_created',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='scheduled_slots_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.patient} in batch {self.batch} is {self.is_active}"
    
class LogScheduler(models.Model):
    room_name = models.ForeignKey(
        RoomDataModel,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='log_scheduler_room_data'
    )
    bed_name = models.ForeignKey(
        BedDataModel,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='log_scheduler_bed_data'
    )

    batch = models.ForeignKey(
        BatchScheduleModel,
        on_delete=models.CASCADE,
        related_name='log_scheduler_batches'
    )

    is_successful = models.BooleanField(default=False)
    is_attended = models.BooleanField(default=False)
    is_failed = models.BooleanField(default=False)
    is_timeout = models.BooleanField(default=False)
    not_patient= models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='log_scheduler_created',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='log_scheduler_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.room_name}:{self.bed_name} in batch {self.batch}"