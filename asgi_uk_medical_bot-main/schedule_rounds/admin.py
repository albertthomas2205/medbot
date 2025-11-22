from django.contrib import admin
from .models import BatchScheduleModel, ScheduledSlots

admin.site.register(BatchScheduleModel)
@admin.register(ScheduledSlots)
class ScheduledSlotsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "batch",
        "is_active",
        "row_number",
        "schedule_order",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    )
    list_filter = ("is_active", "batch", "created_at")
    ordering = ("-created_at",)