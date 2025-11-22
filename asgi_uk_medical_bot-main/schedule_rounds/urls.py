from django.urls import path
from django.conf import settings

from .views import (
    check_scheduled_slots,
    create_scheduler_log,
    export_batch_schedules_excel,
    import_batch_schedules_excel,
    mark_batch_as_completed,
    remove_scheduled_slot,
    schedule_slots,
    swap_room_order_for_scheduled_slot,
    swap_scheduled_slots,
    update_round_schedule,
    update_scheduler_log_attended,
    view_active_scheduled,
    view_active_slot_patient,
    view_all_scheduled,
    view_all_scheduled_slots,
    view_scheduler_logs
)

urlpatterns = [

    path('add-batch-schedule/', update_round_schedule, name='add batches and update them'),
    path('view-all-batch-schedule/', view_all_scheduled, name='view every scheduled'),
    path('view-all-active-batch-schedule/', view_active_scheduled, name='view every active scheduled'),

    path('schedule-slots/', schedule_slots, name='add schedule slots and update them'),
    path('view-all-scheduled-slots/', view_all_scheduled_slots, name='view every scheduled slots'),

    path('check-scheduled-slot/', check_scheduled_slots, name='check scheduled slots'),

    path("swap/scheduled/slots/", swap_scheduled_slots, name="swap_scheduled_slots"),

    path('export_batch_schedules_excel/', export_batch_schedules_excel, name='export batch schedules excel'),
    path('import_batch_schedules_excel/', import_batch_schedules_excel, name='import batch schedules excel'),

    path('mark-batch/completed/<int:batch_id>/', mark_batch_as_completed, name='mark the batch as completed'),
    path('remove/scheduled-slot/', remove_scheduled_slot, name='remove scheduled slot'),

    path('view-active-slot-patient/', view_active_slot_patient, name='view every patient with active and slots available data'),

    path('swap-room-order-scheduled-slot/', swap_room_order_for_scheduled_slot, name='swap room order for scheduled slot url'),

    path('create-scheduler-log/', create_scheduler_log, name='create_scheduler_log'),
    path('update-scheduler-log-attended/', update_scheduler_log_attended, name='update_scheduler_log_attended'),
    path('view-scheduler-logs/', view_scheduler_logs, name='view_scheduler_logs'),

]