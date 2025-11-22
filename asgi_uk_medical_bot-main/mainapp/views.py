# Standard library
import logging
from io import BytesIO

# Third-party
import pandas as pd
from django.db import connection, transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

# Local apps
from .models import HealthcareUser, Patient, LocalIpModel
from schedule_rounds.models import ScheduledSlots
from schedule_rounds.serializers import ScheduledSlotsCreateSerializer
from .serializers import (
    HealthcareUserSerializer,
    PatientSerializer,
    LoginSerializer,
    PatientSlotAssignSerializer,
    LocalIpSerializer,
)
from privilagecontroller.views import hasFeatureAccess

# Logger
logger = logging.getLogger(__name__)


class PatientPagination(PageNumberPagination):
    page_size = 10               # default items per page
    page_size_query_param = 'page_size'  # allow client override ?page_size=20
    max_page_size = 100          # cap the max page size

# Login function
@api_view(['POST'])
@authentication_classes([])  # Disable CSRF-related auth mechanisms
@permission_classes([])  
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response({
            "status": "ok",
            "message": "Login successful",
            "data": serializer.validated_data
        }, status=status.HTTP_200_OK)
    errors = serializer.errors
    first_error = next(iter(errors.values()))[0] if errors else "Invalid input"
    return Response({
        "status": "error",
        "message": first_error
    }, status=status.HTTP_400_BAD_REQUEST)

# Admin/Nurse functions
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_admin_data(request):
    try:
        if request.user.role != 'admin':
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('id')

        if user_id:
            try:
                instance = HealthcareUser.objects.get(id=user_id)
            except HealthcareUser.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'User not found.',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = HealthcareUserSerializer(instance, data=request.data, partial=True)
            operation = "updated"
        else:
            serializer = HealthcareUserSerializer(data=request.data)
            operation = "created"

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': f"User {operation} successfully.",
                'data': serializer.data
            }, status=status.HTTP_200_OK if user_id else status.HTTP_201_CREATED)
        
        errors = {
            field: messages[0]
            for field, messages in serializer.errors.items()
        }

        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            "error": {
                "details": errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in create_or_update_admin_data: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_admin_users(request, role):
    try:
        if request.user.role != 'admin':
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        users = HealthcareUser.objects.filter(role=role)
        serializer = HealthcareUserSerializer(users, many=True)
        return Response({
            'status': 'success',
            'message': 'Users fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_admin_users: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def soft_delete_admin_user(request, user_id):
    try:
        if request.user.role != 'admin':
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        user_instance = HealthcareUser.objects.filter(id=user_id).first()
        if not user_instance:
            return Response({
                'status': 'error',
                'message': 'User not found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        user_instance.is_active = not user_instance.is_active
        user_instance.save()
        action = 'activated' if user_instance.is_active else 'deactivated'
        return Response({
            'status': 'success',
            'message': f"User {action} successfully.",
            'data': None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in soft_delete_admin_user: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Patient functions
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_patient_data(request):
    print("Raw request data:", request.data)
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'patient_data_handling_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        patient_id = request.data.get('id')

        # slot_assigned = request.data.get('slot_assigned')
        # if patient_id:
        #     try:
        #         instance = Patient.objects.get(id=patient_id)
        #     except Patient.DoesNotExist:
        #         return Response({
        #             'status': 'error',
        #             'message': 'Patient not found.',
        #             'data': None
        #         }, status=status.HTTP_404_NOT_FOUND)

        #     if instance.slot_assigned != int(slot_assigned):
        #         bed_taken = Patient.objects.filter(
        #             slot_assigned=slot_assigned,
        #         ).exclude(id=patient_id).exists()

        #         if bed_taken:
        #             error_msg = f"Slot is already allocated to patient"
        #             return Response({
        #                 'status': 'error',
        #                 'message': error_msg,
        #                 'data': None
        #             }, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     bed_taken = Patient.objects.filter(
        #         slot_assigned=slot_assigned
        #     ).exists()

        #     if bed_taken:
        #         error_msg = f"Slot is already allocated to patient"
        #         return Response({
        #             'status': 'error',
        #             'message': error_msg,
        #             'data': None
        #         }, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            if patient_id:
                try:
                    instance = Patient.objects.get(id=patient_id)
                except Patient.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': 'Patient not found.',
                        'data': None
                    }, status=status.HTTP_404_NOT_FOUND)

                serializer = PatientSerializer(instance, data=request.data, partial=True)
                operation = "updated"
            else:
                serializer = PatientSerializer(data=request.data)
                operation = "created"
            if serializer.is_valid():
                updated_instance = serializer.save(
                    is_active=True,
                    updated_by=request.user if patient_id else None,
                    created_by=request.user if not patient_id else None
                )
                updated_instance.save()
                # if not patient_id:
                #     default_times = {
                #         'morning': "06:00:00",
                #         'afternoon': "12:00:00", # ask for fixed time slot or fixed days
                #         'evening': "18:00:00",
                #         'night': "23:59:59",
                #     }
                #     schedules = []
                #     for slot, _ in BatchScheduleModel.TIME_SLOT_CHOICES:
                #         schedules.append(BatchScheduleModel(
                #             patient=updated_instance,
                #             time_slot=slot,
                #             monday=False, tuesday=False, wednesday=False,
                #             thursday=False, friday=False, saturday=False, sunday=False,
                #             trigger_time=default_times[slot],
                #             created_by=request.user
                #         ))
                #     BatchScheduleModel.objects.bulk_create(schedules)
                return Response({
                    'status': 'success',
                    'message': f"Patient {operation} successfully.",
                    'data': serializer.data
                }, status=status.HTTP_200_OK if patient_id else status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'message': "Something went wrong",
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"Exception in create_or_update_patient_data: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_patient(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'patient_data_handling_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        patients = Patient.objects.all().order_by('-created_at')

        paginator = PatientPagination()
        paginated_patients = paginator.paginate_queryset(patients, request)
        serializer = PatientSerializer(paginated_patients, many=True)

        return paginator.get_paginated_response({
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
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def soft_delete_patient(request, patient_id):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'patient_data_handling_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        user_instance = Patient.objects.filter(pk=patient_id).first()
        if not user_instance:
            return Response({
                'status': 'error',
                'message': 'User not found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        user_instance.is_active = not user_instance.is_active
        user_instance.slot_assigned = None
        user_instance.updated_by = request.user
        user_instance.save()

        action = 'activated' if user_instance.is_active else 'deactivated'
        scheduler_data = ScheduledSlots.objects.filter(patient=patient_id).delete()
        slot_taken = ScheduledSlots.objects.filter(patient=user_instance).exists()
        if action == 'deactivated' and slot_taken is True:
            slot_taken = ScheduledSlots.objects.filter(patient=user_instance).first()
            slot_taken.delete()

        return Response({
            'status': 'success',
            'message': f"Patient {action} successfully.",
            'data': None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in soft_delete_admin_user: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def delete_all_patient(request):
    Patient.objects.all().delete()
    return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_designation(request):
    try:
        slot_assigned = request.data.get('slot_assigned')
        patient_id = request.data.get('patient_id')

        # role check
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # feature check
        if not hasFeatureAccess(request.user, 'patient_data_handling_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        if not slot_assigned:
            return Response({
                'status': 'error',
                'message': 'Please select a slot to continue.',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # patient check
        patient = Patient.objects.filter(id=patient_id).first()
        if not patient:
            return Response({
                'status': 'error',
                'message': 'Select a valid patient to assign.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        # slot check
        slot_taken = Patient.objects.filter(slot_assigned=slot_assigned).exclude(id=patient_id).first()
        if slot_taken:
            return Response({
                'status': 'error',
                'message': f"Selected slot is already assigned to : {slot_taken.name}.",
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        scheduler_data = ScheduledSlots.objects.filter(patient=patient).delete()
        # serializer for updating slot
        serializer = PatientSlotAssignSerializer(
            patient, data=request.data, partial=True, context={'updated_by': request.user}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Slot updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in assign_designation: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([AllowAny])
def create_update_local_ip(request):
    try:
        local_ip_add = request.data.get('local_ip')
        port_add = request.data.get('port')

        # if request.user.role not in ['admin', 'nurse']:
        #     return Response({
        #         'status': 'error',
        #         'message': 'Permission denied.',
        #         'data': None
        #     }, status=status.HTTP_403_FORBIDDEN)

        # if not local_ip_add:
        #     return Response({
        #         'status': 'error',
        #         'message': 'Local IP is required.',
        #         'data': None
        #     }, status=status.HTTP_400_BAD_REQUEST)

        # Only one record allowed, so get existing or create new
        local_ip_obj, created = LocalIpModel.objects.get_or_create(pk=1, defaults={'local_ip_add': local_ip_add, 'port':port_add})

        if not created:
            # Update the existing record
            serializer = LocalIpSerializer(local_ip_obj, data={'local_ip_add': local_ip_add, 'port':port_add}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Local IP updated successfully.',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Validation failed.',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'status': 'success',
            'message': 'Local IP created successfully.',
            'data': LocalIpSerializer(local_ip_obj).data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception(f"Exception in create_update_local_ip: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([AllowAny])
def get_local_ip(request):
    try:
        local_ip_obj = LocalIpModel.objects.first()  # get the only record

        if not local_ip_obj:
            return Response({
                'status': 'success',
                'message': 'No local IP found.',
                'data': None
            }, status=status.HTTP_200_OK)

        serializer = LocalIpSerializer(local_ip_obj)
        return Response({
            'status': 'success',
            'message': 'Local IP fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in get_local_ip: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["GET"])
@permission_classes([AllowAny])
def drop_bp2checkme_table(request):
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS vitals_management_bp2checkmemodel CASCADE;")
    print("✅ Dropped table vitals_management_bp2checkmemodel")

@api_view(["GET"])
@permission_classes([AllowAny])
def export_patients_excel(request):
    try:
        patients = Patient.objects.all().values(
            "id", "patient_id", "name", "gender", "age", "is_active"
        ).order_by("id")

        if not patients:
            return HttpResponse(
                "No patient data available.",
                content_type="text/plain",
                status=204
            )
        df = pd.DataFrame(patients)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Patients")

        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="patients.xlsx"'
        return response
    except Exception as e:
        return HttpResponse(
            f"Error generating Excel file: {str(e)}",
            content_type="text/plain",
            status=500
        )
    
@api_view(["POST"])
@permission_classes([AllowAny])
def import_patients_excel(request):
    try:
        # ✅ Check file in request
        if "file" not in request.FILES:
            return Response(
                {"status": "error", "message": "No file uploaded.", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        excel_file = request.FILES["file"]

        # ✅ Read Excel safely
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            logger.exception(f"Invalid Excel file: {e}")
            return Response(
                {"status": "error", "message": "Invalid Excel file.", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Expected columns
        expected_columns = {"id", "patient_id", "name", "gender", "age", "is_active"}
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

        updated, created = 0, 0

        # ✅ Wrap in transaction → all-or-nothing
        with transaction.atomic():
            for _, row in df.iterrows():
                obj, is_created = Patient.objects.update_or_create(
                    id=row["id"],
                    defaults={
                        "patient_id": row["patient_id"],
                        "name": row["name"],
                        "gender": row["gender"],
                        "age": row["age"],
                        "is_active": row["is_active"],
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
        logger.exception(f"Unhandled exception in import_patients_excel: {e}")
        return Response(
            {"status": "error", "message": "Internal server error.", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )