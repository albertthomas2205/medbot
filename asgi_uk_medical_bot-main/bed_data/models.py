from django.db import models
from django.conf import settings

class RoomDataModel(models.Model):
    room_name = models.CharField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='room_created',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='room_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.room_name}"
    
class BedDataModel(models.Model):
    bed_name = models.CharField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='bed_created',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='bed_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.bed_name}"
    
class SlotDataModel(models.Model):
    room_name = models.ForeignKey(
        RoomDataModel,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='room_data'
    )
    bed_name = models.ForeignKey(
        BedDataModel,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='bed_data'
    )

    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    yaw = models.FloatField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='bed_slot_created',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='bed_slot_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['room_name', 'bed_name'],
                name='unique_room_bed_slot'
            )
        ]

    def __str__(self):
        return f"{self.room_name} - {self.bed_name}"
    
class RoomPositionModel(models.Model):
    room_name = models.ForeignKey(
        RoomDataModel,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='room_single_data'
    )
    entry_point_x = models.FloatField(null=True, blank=True)
    entry_point_y = models.FloatField(null=True, blank=True)
    entry_point_yaw = models.FloatField(null=True, blank=True)

    exit_point_x = models.FloatField(null=True, blank=True)
    exit_point_y = models.FloatField(null=True, blank=True)
    exit_point_yaw = models.FloatField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='room_single_created',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='room_single_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['room_name'],
                name='unique_room_slot'
            )
        ]

    def __str__(self):
        return f"{self.room_name} - {self.is_active}"