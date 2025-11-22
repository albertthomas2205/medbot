# Standard library
import itertools
import logging
from io import BytesIO

# Third-party
import pandas as pd
from django.db import connection, transaction
from django.db.models import Case, IntegerField, Max, Value, When
from django.http import HttpResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Local apps
from mainapp.models import Patient
from mainapp.serializers import PatientSerializer
from privilagecontroller.views import hasFeatureAccess
from .models import BatchScheduleModel, ScheduledSlots, LogScheduler
from .serializers import (
    BatchScheduleModelSerializer,
    ScheduledSlotsCreateSerializer,
    ScheduledSlotsSerializer,
    LogSchedulerSerializer
)

# Logger
logger = logging.getLogger(__name__)

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def update_round_schedule(request):
    
    if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

    if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
        return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if pk is provided
    if pk := request.data.get('pk'):  # walrus operator (Python 3.8+)
        try:
            instance = BatchScheduleModel.objects.get(id=pk)
        except BatchScheduleModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Batch schedule not found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BatchScheduleModelSerializer(instance, data=request.data, partial=True)
    else:
        serializer = BatchScheduleModelSerializer(data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save(updated_by=request.user)

        return Response({
            'status': 'success',
            'message': 'Batch schedule updated successfully.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'status': 'error',
        'message': 'Invalid data.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_scheduled(request):
    if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

    if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
        return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

    schedules = BatchScheduleModel.objects.all().order_by('-created_at')
    serializer = BatchScheduleModelSerializer(schedules, many=True)
    
    return Response({
        'status': 'success',
        'message': 'All batch retrieved successfully',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_active_scheduled(request):
    if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

    if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
        return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

    schedules = BatchScheduleModel.objects.filter(is_stopped=False).order_by('-created_at')
    serializer = BatchScheduleModelSerializer(schedules, many=True)
    
    return Response({
        'status': 'success',
        'message': 'All active batch retrieved successfully',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def schedule_slots(request):
    if request.user.role not in ['admin', 'nurse']:
        return Response(
            {'status': 'error', 'message': 'Permission denied.', 'data': None},
            status=status.HTTP_403_FORBIDDEN
        )

    if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
        return Response(
            {'status': 'error', 'message': 'Permission denied.', 'data': None},
            status=status.HTTP_403_FORBIDDEN
        )

    patient_id = request.data.get('patient')
    batch_id = request.data.get('batch')

    if not patient_id or not batch_id:
        return Response(
            {'status': 'error', 'message': 'Patient and Batch are required.', 'data': None},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        batch = BatchScheduleModel.objects.get(pk=batch_id)
        instance = ScheduledSlots.objects.get(patient=patient_id)

        # 🔹 Update batch
        instance.batch = batch
        instance.updated_by = request.user

        # 🔹 Get row_number from patient's assigned room
        patient = instance.patient
        if not patient or not patient.slot_assigned:
            return Response({
                "status": "error",
                "message": "Invalid patient or slot not assigned",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        room = patient.slot_assigned.room_name
        _, row_number = room.room_name.split("_")
        instance.row_number = int(row_number)

        # 🔹 Assign schedule_order
        existing_slot = ScheduledSlots.objects.filter(batch=batch, row_number=row_number).exclude(pk=instance.pk).first()
        if existing_slot:
            # reuse the existing order for this row_number
            schedule_order = existing_slot.schedule_order
        else:
            # assign next available order
            max_order = ScheduledSlots.objects.filter(batch=batch_id).aggregate(Max("schedule_order"))["schedule_order__max"]
            schedule_order = 1 if max_order is None else max_order + 1
           
        instance.schedule_order = schedule_order
        instance.save()

        return Response({
            'status': 'success',
            'message': f'Patient {instance.patient.name} moved to batch {instance.batch.batch_name} successfully.',
            'data': ScheduledSlotsSerializer(instance).data
        }, status=status.HTTP_200_OK)

    except ScheduledSlots.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Slot schedule not found for this patient.',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_scheduled_slots(request):
    if request.user.role not in ['admin', 'nurse']:
        return Response(
            {'status': 'error', 'message': 'Permission denied.', 'data': None},
            status=status.HTTP_403_FORBIDDEN
        )

    if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
        return Response(
            {'status': 'error', 'message': 'Permission denied.', 'data': None},
            status=status.HTTP_403_FORBIDDEN
        )

    # Fetch schedules ordered by id
    schedules = (
        ScheduledSlots.objects
        .select_related('patient', 'batch')
        .all()
        .order_by(
            # 'schedule_order', 
            'row_number', 
            'id')
    )
    serializer = ScheduledSlotsSerializer(schedules, many=True)

    response_data = []
    for row_number, items in itertools.groupby(serializer.data, key=lambda x: x['row_number']):
        response_data.append({
            "row_number": row_number,
            "slots": list(items)
        })

    return Response({
        'status': 'success',
        'message': 'All scheduled slots retrieved successfully',
        'data': response_data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_scheduled_slots(request):
    if request.user.role not in ['admin', 'nurse']:
        return Response(
            {'status': 'error', 'message': 'Permission denied.', 'data': None},
            status=status.HTTP_403_FORBIDDEN
        )

    if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
        return Response(
            {'status': 'error', 'message': 'Permission denied.', 'data': None},
            status=status.HTTP_403_FORBIDDEN
        )
    
    patient_id = request.data.get('patient')
    batch_id = request.data.get('batch')

    if not patient_id or not batch_id:
        return Response(
            {'status': 'error', 'message': 'Patient and Batch are required.', 'data': None},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        scheduled_slot = ScheduledSlots.objects.select_related("batch").get(patient=patient_id)
        batch_data = BatchScheduleModel.objects.get(pk=batch_id)
        batchName = batch_data.batch_name

        if scheduled_slot.batch.pk == int(batch_id):
            return Response(
                {'status': 'error', 'message': 'The patient already exists in this batch slot.', 'data': None},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # different batch
            return Response(
                {
                    'status': 'warning',
                    'message': f"Patient already exists in batch {scheduled_slot.batch.batch_name}. "
                               f"Do you want to switch them to batch {batchName}?",
                    'data': {
                        'current_batch': scheduled_slot.batch.pk,
                        'requested_batch': int(batch_id),
                        'patient_id': int(patient_id)
                    }
                },
                status=status.HTTP_200_OK
            )

    except ScheduledSlots.DoesNotExist:
        patient = Patient.objects.filter(pk=patient_id).first()
        if not patient or not patient.slot_assigned:
            return Response({
                "status": "error",
                "message": "Invalid patient or slot not assigned",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        room = patient.slot_assigned.room_name
        _, row_number = room.room_name.split("_")

        serializer = ScheduledSlotsCreateSerializer(data=request.data, partial=True)
        batch_data = BatchScheduleModel.objects.get(pk=batch_id)
        if serializer.is_valid():
            existing_slot = ScheduledSlots.objects.filter(
                batch=batch_data, 
                row_number=row_number).first()

            max_order = None 
            schedule_order = None
            if existing_slot:
                # Reuse its order (all slots in same row_number share same order)
                schedule_order = existing_slot.schedule_order
            else:
                # Assign a new order = max existing + 1
                max_order = ScheduledSlots.objects.filter(batch=batch_id).aggregate(Max("schedule_order"))["schedule_order__max"]
                schedule_order = max_order + 1 if max_order is not None else 1

            slot = serializer.save(
                updated_by=request.user,
                row_number=row_number,
                schedule_order=schedule_order - 1
            )

            return Response({
                "status": "success",
                "message": "scheduled slot assigned successfully",
                "data": ScheduledSlotsSerializer(slot).data,
                "max_order": max_order if max_order is not None else 0,
                "schedule_order": schedule_order
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Invalid data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def swap_scheduled_slots(request):
    try:
        id1 = request.data.get("pk1")
        id2 = request.data.get("pk2")

        if not id1 or not id2:
            return Response(
                {"status": "error", "message": "Both pk1 and pk2 are required.", "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            slot1 = ScheduledSlots.objects.select_related("patient", "batch").get(pk=id1)
            slot2 = ScheduledSlots.objects.select_related("patient", "batch").get(pk=id2)
        except ScheduledSlots.DoesNotExist:
            return Response(
                {"status": "error", "message": "One or both slots not found.", "data": None},
                status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            # Extract current patient IDs
            p1 = slot1.patient_id
            p2 = slot2.patient_id

            # Generate a temp patient id that won't collide (negative number)
            temp_id = -1 * int(get_random_string(6, allowed_chars="123456789"))

            with connection.cursor() as cursor:
                # Step 1: Move slot1.patient -> temp_id
                cursor.execute(
                    "UPDATE schedule_rounds_scheduledslots SET patient_id = %s WHERE id = %s",
                    [temp_id, id1]
                )
                # Step 2: Move slot2.patient -> slot1.patient
                cursor.execute(
                    "UPDATE schedule_rounds_scheduledslots SET patient_id = %s WHERE id = %s",
                    [p1, id2]
                )
                # Step 3: Move temp_id -> slot2.patient
                cursor.execute(
                    "UPDATE schedule_rounds_scheduledslots SET patient_id = %s WHERE id = %s",
                    [p2, id1]
                )

        # Refresh objects
        slot1.refresh_from_db()
        slot2.refresh_from_db()

        return Response({
            "status": "success",
            "message": f"Swapped patients between slots {id1} and {id2}",
            "data": {
                "slot1": {
                    "id": slot1.id,
                    "patient": str(slot1.patient),
                    "batch": str(slot1.batch),
                },
                "slot2": {
                    "id": slot2.id,
                    "patient": str(slot2.patient),
                    "batch": str(slot2.batch),
                }
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in swap_scheduled_slots: {e}")
        return Response(
            {'status': 'error', 'message': 'Internal server error.', 'data': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
@permission_classes([AllowAny])
def export_batch_schedules_excel(request):
    try:
        schedules = BatchScheduleModel.objects.all().values(
            "id", "batch_name", "time_slot", "monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday", "trigger_time",
            "is_stopped", "is_notified", "completed_time"
        ).order_by('id')

        if not schedules:
            return Response(
                "No batch schedules available.",
                content_type="text/plain",
                status=204
            )

        df = pd.DataFrame(schedules)

        # ✅ Convert timezone-aware datetimes to naive or string
        if "completed_time" in df.columns:
            df["completed_time"] = df["completed_time"].apply(
                lambda x: x.replace(tzinfo=None) if pd.notnull(x) else None
            )

        # Write to memory buffer
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="BatchSchedules")

        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="batch_schedules.xlsx"'
        return response

    except Exception as e:
        return Response(
            f"Error generating Excel file: {str(e)}",
            content_type="text/plain",
            status=500
        )

@api_view(["POST"])
@permission_classes([AllowAny])
def import_batch_schedules_excel(request):
    try:
        if "file" not in request.FILES:
            return Response(
                {"status": "error", "message": "No file uploaded.", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        excel_file = request.FILES["file"]

        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            logger.exception(f"Invalid Excel file: {e}")
            return Response(
                {"status": "error", "message": "Invalid Excel file.", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expected_columns = {
            "id", "batch_name", "time_slot", "monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday", "trigger_time",
            "is_stopped"
        }
        missing = expected_columns - set(df.columns)
        if missing:
            return Response(
                {
                    "status": "error",
                    "message": f"Missing required columns: {', '.join(missing)}",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if df.empty:
            return Response(
                {"status": "error", "message": "Excel file is empty.", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created, updated = 0, 0
        with transaction.atomic():
            for _, row in df.iterrows():
                obj, is_created = BatchScheduleModel.objects.update_or_create(
                    id=row["id"],
                    defaults={
                        "batch_name": row["batch_name"],
                        "time_slot": row["time_slot"],
                        "monday": row["monday"],
                        "tuesday": row["tuesday"],
                        "wednesday": row["wednesday"],
                        "thursday": row["thursday"],
                        "friday": row["friday"],
                        "saturday": row["saturday"],
                        "sunday": row["sunday"],
                        "trigger_time": row["trigger_time"],
                        "is_stopped": row["is_stopped"],
                    },
                )
                if is_created:
                    created += 1
                else:
                    updated += 1

        return Response(
            {
                "status": "success",
                "message": f"Import completed: {created} created, {updated} updated.",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"Unhandled exception in import_batch_schedules_excel: {e}")
        return Response(
            {"status": "error", "message": "Internal server error.", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@api_view(['PUT'])
@permission_classes([AllowAny])
def mark_batch_as_completed(request, batch_id):
    try:
        schedules = BatchScheduleModel.objects.get(pk=batch_id)
    except BatchScheduleModel.DoesNotExist:
        return Response({
            "status": "error",
            "message": f"Batch with id {batch_id} not found.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)

    schedules.completed_time = timezone.now()
    schedules.is_notified = True
    schedules.save()

    serializer = BatchScheduleModelSerializer(schedules)

    return Response({
        "status": "success",
        "message": "Batch marked as completed successfully.",
        "data": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_scheduled_slot(request):
    try:
        slot_id = request.data.get('slot_id')

        # role check
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # feature check
        if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        slot_taken = ScheduledSlots.objects.filter(pk=slot_id).first()
        if not slot_taken:
            return Response({
                'status': 'error',
                'message': f"Selected patient does not exist in the slot",
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        slot_taken.delete()
        return Response({
            'status': 'success',
            'message': 'Slot updated successfully.',
            'data': None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in assign_designation: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_active_slot_patient(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        patients = (
            Patient.objects
            .filter(slot_assigned__isnull=False, is_active=True)
            .order_by('-created_at')
        )
        serializer = PatientSerializer(patients, many=True)

        return Response({
            'status': 'success',
            'message': 'Patients fetched successfully.',
            'data': serializer.data
        })

    except Exception as e:
        logger.exception(f"Exception in view_all_patient: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def swap_room_order_for_scheduled_slot(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        room_order_a = request.data.get('room_pos_a')
        room_order_b = request.data.get('room_pos_b')
        batch_id = request.data.get('batch_id')

        if not room_order_a or not room_order_b or not batch_id:
            return Response(
                {'status': 'error', 'message': 'room_pos_a, room_pos_b, and batch_id are required.', 'data': None},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            room_order_a = int(room_order_a)
            room_order_b = int(room_order_b)
        except (TypeError, ValueError):
            return Response(
                {'status': 'error', 'message': 'room_pos_a and room_pos_b must be integers.', 'data': None},
                status=status.HTTP_400_BAD_REQUEST
            )

        if room_order_a == room_order_b:
            return Response(
                {'status': 'error', 'message': 'Both room positions are the same, nothing to swap.', 'data': None},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            updated_count = ScheduledSlots.objects.filter(
                schedule_order__in=[room_order_a, room_order_b],
                batch=batch_id
            ).update(
                schedule_order=Case(
                    When(schedule_order=room_order_a, then=Value(room_order_b)),
                    When(schedule_order=room_order_b, then=Value(room_order_a)),
                    output_field=IntegerField()
                )
            )

        if updated_count == 0:
            return Response({
                'status': 'error',
                'message': 'No matching slots found for given room positions.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'status': 'success',
            'message': f'Successfully swapped schedule_order {room_order_a} and {room_order_b}.',
            'data': None
        })

    except Exception as e:
        logger.exception(f"Exception in swap_room_order_for_scheduled_slot: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
@permission_classes([AllowAny])
def create_scheduler_log(request):
    try:
        # if request.user.role not in ['admin', 'nurse']:
        #     return Response({
        #         'status': 'error',
        #         'message': 'Permission denied.',
        #         'data': None
        #     }, status=status.HTTP_403_FORBIDDEN)

        # if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
        #     return Response({
        #         'status': 'error',
        #         'message': 'Permission denied.',
        #         'data': None
        #     }, status=status.HTTP_403_FORBIDDEN)

        serializer = LogSchedulerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Log created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'error',
            'message': serializer.errors,
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in create_scheduler_log: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_scheduler_log_attended(request):
    try:
        log_id = request.data.get('log_id')
        is_attended = request.data.get('is_attended')

        if log_id is None or is_attended is None:
            return Response({
                'status': 'error',
                'message': 'log_id and is_attended are required.',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # if request.user.role not in ['admin', 'nurse']:
        #     return Response({
        #         'status': 'error',
        #         'message': 'Permission denied.',
        #         'data': None
        #     }, status=status.HTTP_403_FORBIDDEN)

        # if not hasFeatureAccess(request.user, 'batch_schedule_crud'):
        #     return Response({
        #         'status': 'error',
        #         'message': 'Permission denied.',
        #         'data': None
        #     }, status=status.HTTP_403_FORBIDDEN)

        log_entry = LogScheduler.objects.filter(pk=log_id).first()
        if not log_entry:
            return Response({
                'status': 'error',
                'message': 'Log not found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LogSchedulerSerializer(log_entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Log updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'success',
            'message': 'Log updated successfully.',
            'data': LogSchedulerSerializer(log_entry).data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in update_scheduler_log_attended: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([AllowAny])
def view_scheduler_logs(request):
    try:
        # if request.user.role not in ['admin', 'nurse']:
        #     return Response({
        #         'status': 'error',
        #         'message': 'Permission denied.',
        #         'data': None
        #     }, status=status.HTTP_403_FORBIDDEN)

        logs = LogScheduler.objects.all().order_by('-created_at')
        serializer = LogSchedulerSerializer(logs, many=True)

        return Response({
            'status': 'success',
            'message': 'Logs fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_scheduler_logs: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)