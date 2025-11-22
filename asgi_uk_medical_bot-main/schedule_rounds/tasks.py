# Standard library
import itertools
import logging
import re
import os

# Third-party
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime

# Local application
from .models import BatchScheduleModel, ScheduledSlots
from .serializers import ScheduledSlotsSchedulerSerializer
from bed_data.models import RoomDataModel, RoomPositionModel

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, 'logs', 'app.log')

def extract_number(value: str) -> int:
    """Extracts the trailing number from 'room_10' or 'bed_5'. Defaults to 0 if no number."""
    match = re.search(r"(\d+)$", value)
    return int(match.group(1)) if match else 0

@shared_task(bind=True, max_retries=3)
def check_and_send_schedules(self):
    try:
        now = timezone.localtime()

        key = f"check_schedule_lock_{now.strftime('%Y%m%d%H%M')}"
        if not cache.add(key, "locked", timeout=60):
            logger.exception("Another worker already processed this minute, skipping...")
            return

        weekday = now.strftime("%A").lower()
        schedules = BatchScheduleModel.objects.filter(**{weekday: True}, is_stopped=False)

        if not schedules.exists():
            logger.exception(f"No schedules found for weekday={weekday}")
            return

        for schedule in schedules:
            try:
                if schedule.trigger_time.hour != now.hour or schedule.trigger_time.minute != now.minute:
                    logger.debug(
                        f"Schedule {schedule.id} trigger time not due yet "
                        f"({schedule.trigger_time}) vs now {now.hour}:{now.minute}"
                    )
                    continue

                logger.exception(f"✅ Processing schedule {schedule.pk} - {schedule.batch_name}")

                batch_id = schedule.pk

                try:
                    # Fetch schedules ordered by id
                    schedules = (
                        ScheduledSlots.objects.filter(batch=schedule)
                        # .select_related('patient', 'batch')
                        .prefetch_related('patient__slot_assigned')
                        .all()
                        .order_by(
                            # 'schedule_order', 
                            'row_number', 
                            'id')
                    )
                    serializer = ScheduledSlotsSchedulerSerializer(schedules, many=True)

                    response_data = []
                    for row_number, items in itertools.groupby(serializer.data, key=lambda x: x['row_number']):
                        room_merged = f"room_{row_number}"
                        room_data = RoomDataModel.objects.get(room_name=room_merged)
                        room_position = RoomPositionModel.objects.get(room_name=room_data)
                        
                        slots_with_pos = []
                        for slot_item in items:
                            slot_data = slot_item['slot']
                            slots_with_pos.append({
                                # "id": slot_data['id'],
                                "bed_name": slot_data['bed_name']['bed_name'],
                                "x": slot_data['x'],
                                "y": slot_data['y'],
                                "yaw": slot_data['yaw']
                            })

                        response_data.append({
                            # "row_number": row_number,
                            room_merged : {
                                "entry_point_x": room_position.entry_point_x,
                                "entry_point_y": room_position.entry_point_y,
                                "entry_point_yaw": room_position.entry_point_yaw,
                                "exit_point_x": room_position.exit_point_x,
                                "exit_point_y": room_position.exit_point_y,
                                "exit_point_yaw": room_position.exit_point_yaw,
                            },
                            # "slots": list(items),
                            "slot_pos": slots_with_pos
                        })

                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        "scheduler_value_group",
                        {
                            "type": "scheduler_value_message",
                            "payload": {
                                "scheduler": response_data,
                                "batch_id": batch_id
                            }
                        },
                    )

                except Exception as e:
                    logger.exception(f"Error fetching slots for schedule {e}", exc_info=True)
                    continue

            except Exception as e:
                logger.exception(f"Unexpected error processing schedule {schedule.id}: {e}", exc_info=True)
                continue

    except Exception as e:
        logger.critical(f"Critical error in check_and_send_schedules: {e}", exc_info=True)
        # Retry task in 1 minute if it fails
        try:
            self.retry(countdown=60, exc=e)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for check_and_send_schedules", exc_info=True)

@shared_task(bind=True, max_retries=3)
def reset_completed_time(self):
    """
    Reset completed_time on Monday at 1 AM.
    """
    try:
        # now = timezone.localtime()

        # weekday = now.strftime("%A").lower()

        # latest_record = RobotTelemetry.objects.order_by('-id').first()

        # if weekday == latest_record.batch_refresh_week:
        updated_count = BatchScheduleModel.objects.update(completed_time= None, is_notified= False)
        logger.info(f"✅ Reset completed_time for {updated_count} schedules on Monday")
    except Exception as e:
        logger.critical(f"Critical error in reset_completed_time: {e}", exc_info=True)
        try:
            self.retry(countdown=300, exc=e)  # retry after 5 minutes if failed
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for reset_completed_time", exc_info=True)

@shared_task(bind=True, max_retries=3)
def clear_log_file(self):
    """
    Clears the content of app.log at the start of every month.
    """
    try:
        logger = logging.getLogger('django')

        # Close and remove existing file handlers for app.log
        for handler in list(logger.handlers):
            if hasattr(handler, 'baseFilename') and handler.baseFilename == LOG_FILE_PATH:
                handler.close()
                logger.removeHandler(handler)

        # Delete the file
        if os.path.exists(LOG_FILE_PATH):
            os.remove(LOG_FILE_PATH)

        # Recreate empty file
        open(LOG_FILE_PATH, 'w').close()

        # Re-add file handler
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        file_handler.setFormatter(logging.Formatter('[{asctime}] {levelname} {name} - {message}', style='{'))
        logger.addHandler(file_handler)

        logger.info("🧹 Cleared app.log safely")
    except Exception as e:
        logger.critical(f"Critical error while clearing log file: {e}", exc_info=True)
        try:
            self.retry(countdown=300, exc=e)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for clear_log_file", exc_info=True)
