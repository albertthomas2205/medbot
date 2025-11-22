import struct
import logging
from io import BytesIO

import numpy as np
from PIL import Image

from django.core.files.base import ContentFile
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from mainapp.models import Patient, AlertHistory
from mainapp.serializers import PatientSerializer, AlertHistorySerializer
from bed_data.models import RoomPositionModel, SlotDataModel, RoomDataModel, BedDataModel
from bed_data.serializer import RoomPositionModelSerializer, SlotCoordinatesSerializer

from .models import (
    RobotTelemetry,
    ArmEndpose,
    JointVelocity,
    JointEffort,
    JointPosition,
    ArmStatus,
    JointStatus,
    FailedScheduledModel,
    BatteryStatus,
    MapManagement,
    JointHeat
)
from .serializers import (
    RobotTelemetryLastSlotSerializer,
    RobotTelemetrySerializer,
    RobotTelemetryLastMapSerializer,
    ArmEndposeSerializer,
    JointVelocitySerializer,
    JointEffortSerializer,
    JointPositionSerializer,
    ArmStatusSerializer,
    JointStatusSerializer,
    RobotTelemetryLastStatusSerializer,
    RobotTelemetryLastVolumeSerializer,
    RobotTelemetryLastRobotEmergencySerializer,
    FailedScheduledModelSerializer,
    RobotTelemetryLastRobotRoomOpeningSerializer,
    BatteryStatusSerializer,
    MapManagementSerializer,
    JointHeatSerializer
)

from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

class AlertPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class FailedSchedulesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

@api_view(['GET'])
@permission_classes([AllowAny])
def get_patient_data(request, patient_id):
    try:
        Patient_data = Patient.objects.get(id=patient_id)
        serializer = PatientSerializer(Patient_data)
        return Response({
            'status': 'success',
            'message': 'Patient data fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_privileges: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_room_entry_cord(request, room):
    try:
        room = RoomDataModel.objects.get(room_name=room)
        room_cor = RoomPositionModel.objects.get(room_name=room.id)
        serializer = RoomPositionModelSerializer(room_cor)
        return Response({
            'status': 'success',
            'message': 'Room entry point fetched successfully.',
            'data': serializer.data['entry_point']
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_privileges: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_room_exit_cord(request, room):
    try:
        room = RoomDataModel.objects.get(room_name=room)
        room_cor = RoomPositionModel.objects.get(room_name=room.id)
        serializer = RoomPositionModelSerializer(room_cor)
        return Response({
            'status': 'success',
            'message': 'Room exit point fetched successfully.',
            'data': serializer.data['exit_point']
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_privileges: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_slot_cord(request, room, bed):
    try:
        room = RoomDataModel.objects.get(room_name=room)
        bed = BedDataModel.objects.get(bed_name=bed)
        slot_cor = SlotDataModel.objects.get(room_name=room.id, bed_name=bed.id)
        serializer = SlotCoordinatesSerializer(slot_cor)
        return Response({
            'status': 'success',
            'message': 'Slot fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_privileges: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def save_help(request):
    try:
        room = request.data.get("room")
        bed = request.data.get("bed")

        if not room or not bed:
            return Response({
                "status": "error",
                "message": "Both room and bed are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract the boolean flags
        is_timed_out = request.data.get("is_timed_out", False)
        is_help = request.data.get("is_help", False)
        is_cancelled = request.data.get("is_cancelled", False)
        not_me = request.data.get("not_me", False)

        # Ensure they are treated as booleans
        flags = [bool(is_timed_out), bool(is_help), bool(is_cancelled), bool(not_me)]
        true_count = sum(1 for val in flags if val)

        # Validation: exactly one should be True
        if true_count != 1:
            return Response({
                "status": "error",
                "message": "Exactly one of is_timed_out, is_help, is_cancelled, or not_me must be True."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AlertHistorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Alert saved successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in save_help: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def respond_alert(request, alert_id, rsp):
    try:
        alert = AlertHistory.objects.get(id=alert_id)
        if rsp == 1:
            alert.responded = True
        else:
            alert.is_timed_out = True
        alert.save()

        serializer = AlertHistorySerializer(alert)

        return Response({
            "status": "success",
            "message": "Alert marked as responded.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except AlertHistory.DoesNotExist:
        return Response({
            "status": "error",
            "message": f"Alert with id {alert_id} not found."
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.exception(f"Exception in respond_alert: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def view_active_alerts(request):
    try:
        alerts = AlertHistory.objects.filter(
            Q(reason__isnull=True) | Q(reason="") | Q(responded=False)
        ).order_by("-created_at")
        serializer = AlertHistorySerializer(alerts, many=True)

        return Response({
            "status": "success",
            "message": "Active alerts fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_active_alerts: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def view_all_alerts(request):
    try:
        alerts = AlertHistory.objects.all().order_by("-created_at")
        paginator = AlertPagination()
        paginated_alerts = paginator.paginate_queryset(alerts, request)
        serializer = AlertHistorySerializer(paginated_alerts, many=True, context={"request":request})
        return paginator.get_paginated_response({
            'status': 'success',
            'message': 'All BP2CheckMe records retrieved successfully',
            'data': serializer.data
        })
    except Exception as e:
        logger.exception(f"Exception in view_all_alerts: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_alert_reason(request, pk):
    try:
        alert = AlertHistory.objects.get(pk=pk)

        reason = request.data.get("reason")
        if not reason:
            return Response({
                "status": "error",
                "message": "Reason is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        alert.reason = reason
        alert.responded = True
        alert.save()

        serializer = AlertHistorySerializer(alert)

        return Response({
            "status": "success",
            "message": "Reason updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except AlertHistory.DoesNotExist:
        return Response({
            "status": "error",
            "message": f"Alert with id {pk} not found."
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.exception(f"Exception in update_alert_reason: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def fetch_latest_slot(request):
    try:
        instance = RobotTelemetry.objects.get(pk=1)

        serializer = RobotTelemetryLastSlotSerializer(instance)

        return Response({
            "status": "success",
            "message": "Latest room and bed fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def robot_telemetry_all(request):
#     try:
#         instance = RobotTelemetry.objects.all()

#         serializer = RobotTelemetrySerializer(instance)

#         return Response({
#             "status": "success",
#             "message": "Robot Telemetry fetched successfully.",
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         logger.exception(f"Exception: {e}")
#         return Response({
#             "status": "error",
#             "message": "Internal server error.",
#             "data": str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def robot_telemetry_all(request):
    try:
        instances = RobotTelemetry.objects.all()
        if not instances.exists():  # Check if queryset is empty
            return Response({
                "status": "error",
                "message": "No robot telemetry data found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RobotTelemetrySerializer(instances, many=True)
        return Response({
            "status": "success",
            "message": "Robot Telemetry fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
@permission_classes([AllowAny])
def save_stcm_map(request):
    try:
        stcm_file = request.FILES.get("stcm_file")
        if not stcm_file:
            return Response(
                {"status": "error", "message": "STCM file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        instance = RobotTelemetry.objects.order_by('-id').first()
        if not instance:
            return Response(
                {"status": "error", "message": "No RobotTelemetry record found to attach the file."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            instance.robot_map_file = stcm_file
            instance.save()
            # ✅ Success response added here
            return Response(
                {"status": "success", "message": "STCM file uploaded successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.exception("Failed to save STCM file")
            return Response(
                {"status": "error", "message": f"Failed to save file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    except Exception as e:
        logger.exception(f"Exception: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ---- Helper to fetch pk=1 ----
def get_single_instance(model):
    obj, _ = model.objects.get_or_create(pk=1)  # ensures row exists
    return obj


# ---- ArmEndpose ----
@api_view(["GET", "PUT"])
@permission_classes([AllowAny])
def arm_endpose(request):
    try:
        instance = get_single_instance(ArmEndpose)

        if request.method == "GET":
            serializer = ArmEndposeSerializer(instance)
            return Response({"status": "success", "data": serializer.data})

        elif request.method == "PUT":
            serializer = ArmEndposeSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "arm_endpose_value_group",
                    {
                        "type": "arm_endpose_value_message",
                        "payload": {
                            "x": obj.x,
                            "y": obj.y,
                            "z": obj.z,
                            "rx": obj.rx,
                            "ry": obj.ry,
                            "rz": obj.rz,
                        }
                    },
                )

                return Response({"status": "success", "message": "Updated", "data": serializer.data})
            return Response({"status": "error", "errors": serializer.errors}, status=400)

    except Exception as e:
        logger.exception(f"ArmEndpose error: {e}")
        return Response({"status": "error", "message": str(e)}, status=500)


# ---- JointVelocity ----
@api_view(["GET", "PUT"])
@permission_classes([AllowAny])
def joint_velocity(request):
    try:
        instance = get_single_instance(JointVelocity)

        if request.method == "GET":
            serializer = JointVelocitySerializer(instance)
            return Response({"status": "success", "data": serializer.data})

        elif request.method == "PUT":
            serializer = JointVelocitySerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "joint_velocity_value_group",
                    {
                        "type": "joint_velocity_value_message",
                        "payload": {
                            "j1": obj.j1,
                            "j2": obj.j2,
                            "j3": obj.j3,
                            "j4": obj.j4,
                            "j5": obj.j5,
                            "j6": obj.j6,
                        }
                    },
                )

                return Response({"status": "success", "message": "Updated", "data": serializer.data})
            return Response({"status": "error", "errors": serializer.errors}, status=400)

    except Exception as e:
        logger.exception(f"JointVelocity error: {e}")
        return Response({"status": "error", "message": str(e)}, status=500)


# ---- JointEffort ----
@api_view(["GET", "PUT"])
@permission_classes([AllowAny])
def joint_effort(request):
    try:
        instance = get_single_instance(JointEffort)

        if request.method == "GET":
            serializer = JointEffortSerializer(instance)
            return Response({"status": "success", "data": serializer.data})

        elif request.method == "PUT":
            serializer = JointEffortSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "joint_effort_value_group",
                    {
                        "type": "joint_effort_value_message",
                        "payload": {
                            "j1": obj.j1,
                            "j2": obj.j2,
                            "j3": obj.j3,
                            "j4": obj.j4,
                            "j5": obj.j5,
                            "j6": obj.j6,
                        }
                    },
                )

                return Response({"status": "success", "message": "Updated", "data": serializer.data})
            return Response({"status": "error", "errors": serializer.errors}, status=400)

    except Exception as e:
        logger.exception(f"JointEffort error: {e}")
        return Response({"status": "error", "message": str(e)}, status=500)


# ---- JointPosition ----
@api_view(["GET", "PUT"])
@permission_classes([AllowAny])
def joint_position(request):
    try:
        instance = get_single_instance(JointPosition)

        if request.method == "GET":
            serializer = JointPositionSerializer(instance)
            return Response({"status": "success", "data": serializer.data})

        elif request.method == "PUT":
            serializer = JointPositionSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "joint_position_value_group",
                    {
                        "type": "joint_position_value_message",
                        "payload": {
                            "j1": obj.j1,
                            "j2": obj.j2,
                            "j3": obj.j3,
                            "j4": obj.j4,
                            "j5": obj.j5,
                            "j6": obj.j6,
                        }
                    },
                )

                return Response({"status": "success", "message": "Updated", "data": serializer.data})
            return Response({"status": "error", "errors": serializer.errors}, status=400)

    except Exception as e:
        logger.exception(f"JointPosition error: {e}")
        return Response({"status": "error", "message": str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def create_or_update_arm_status(request):
    try:
        try:
            instance = ArmStatus.objects.order_by('-id').first()
        except ArmStatus.DoesNotExist:
            instance = None

        serializer = ArmStatusSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "refresh_arm_data_value_group",
                {
                    "type": "refresh_arm_data_value_message",
                    "payload": True
                },
            )

            return Response(
                {
                    "status": "success",
                    "message": "ArmStatus updated" if instance else "ArmStatus created",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        logger.exception(f"ArmStatus error: {e}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_arm_status(request):
    try:
        instance = ArmStatus.objects.order_by('-id').first()
        if not instance:
            return Response(
                {"status": "error", "message": "No ArmStatus found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ArmStatusSerializer(instance)
        return Response(
            {
                "status": "success",
                "message": "Latest ArmStatus fetched",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"ArmStatus fetch error: {e}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@api_view(['POST'])
@permission_classes([AllowAny])
def create_or_update_joint_status(request):
    try:
        try:
            joint_num = request.data.get('joint_number')
            instance = JointStatus.objects.get(joint_number=joint_num)
        except JointStatus.DoesNotExist:
            instance = None

        serializer = JointStatusSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "refresh_joint_data_value_group",
                {
                    "type": "refresh_joint_data_value_message",
                    "payload": True
                },
            )

            return Response(
                {
                    "status": "success",
                    "message": "JointStatus updated" if instance else "JointStatus created",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        logger.exception(f"JointStatus error: {e}")
        return Response(
            {"status": "error", "message": "Internal server error", 'data':str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_joint_status(request):
    try:
        instance = JointStatus.objects.order_by('-id').first()
        if not instance:
            return Response(
                {"status": "error", "message": "No JointStatus found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = JointStatusSerializer(instance)
        return Response(
            {
                "status": "success",
                "message": "Latest JointStatus fetched",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"ArmStatus fetch error: {e}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def getup_robot_status(request):
    try:
        # Fetch the latest telemetry record
        instance = RobotTelemetry.objects.order_by('-id').first()
        if not instance:
            return Response(
                {"status": "error", "message": "No RobotTelemetry found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == "GET":
            serializer = RobotTelemetryLastStatusSerializer(instance)
            return Response(
                {
                    "status": "success",
                    "message": "Latest RobotTelemetry status fetched",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        elif request.method == "PUT":
            serializer = RobotTelemetryLastStatusSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "RobotTelemetry status updated",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        logger.exception(f"RobotTelemetry status fetch/update error: {e}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def getup_volume_status(request):
    try:
        # Fetch the latest telemetry record
        instance = RobotTelemetry.objects.order_by('-id').first()
        if not instance:
            return Response(
                {"status": "error", "message": "No RobotTelemetry found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == "GET":
            serializer = RobotTelemetryLastVolumeSerializer(instance)
            return Response(
                {
                    "status": "success",
                    "message": "Latest RobotTelemetry volume fetched",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        elif request.method == "PUT":
            serializer = RobotTelemetryLastVolumeSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "RobotTelemetry volume updated",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        logger.exception(f"RobotTelemetry status fetch/update error: {e}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def getup_robot_emergency_status(request):
    try:
        # Fetch the latest telemetry record
        instance = RobotTelemetry.objects.order_by('-id').first()
        if not instance:
            return Response(
                {"status": "error", "message": "No RobotTelemetry found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == "GET":
            serializer = RobotTelemetryLastRobotEmergencySerializer(instance)
            return Response(
                {
                    "status": "success",
                    "message": "Latest RobotTelemetry robot emergency fetched",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        elif request.method == "PUT":
            robot_emergency = request.data.get("robot_emergency", instance.robot_emergency)
            instance.robot_emergency = robot_emergency

            serializer = RobotTelemetryLastRobotEmergencySerializer(
                instance, data={"robot_emergency": robot_emergency}, partial=True
            )
            if serializer.is_valid():
                serializer.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "emergency_value_group",
                    {
                        "type": "emergency_value_message",
                        "payload": {
                            "emergency": instance.robot_emergency
                        }
                    },
                )

                if instance.robot_emergency is True:
                    emergency_state = "pressed"
                else:
                    emergency_state = "released"
                
                return Response(
                    {
                        "status": "success",
                        "message": f"Robot emergency button {emergency_state}",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        logger.exception(f"RobotTelemetry status fetch/update error: {e}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@api_view(['POST'])
@permission_classes([AllowAny])
def create_or_update_robot_telemetry(request):
    try:
        instance = RobotTelemetry.objects.order_by('-id').first()

        serializer = RobotTelemetrySerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "RobotTelemetry updated" if instance else "RobotTelemetry created",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        logger.exception(f"RobotTelemetry error: {e}")
        return Response(
            {"status": "error", "message": "Internal server error", "data": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def failed_scheduled_list_create(request):
    try:
        if request.method == 'GET':
            failed_schedules = FailedScheduledModel.objects.all().order_by('-created_at')
            paginator = FailedSchedulesPagination()
            paginated_alerts = paginator.paginate_queryset(failed_schedules, request)
            serializer = FailedScheduledModelSerializer(paginated_alerts, many=True)
            return paginator.get_paginated_response({
                "status": "success",
                "message": "Failed schedules fetched successfully.",
                "data": serializer.data
            })

        elif request.method == 'POST':
            serializer = FailedScheduledModelSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Failed schedule created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in failed_scheduled_list_create: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
@permission_classes([AllowAny])
def failed_scheduled_mark_respond(request, pk):
    try:
        schedule = get_object_or_404(FailedScheduledModel, pk=pk)
        serializer = FailedScheduledModelSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Failed schedule updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in failed_scheduled_detail: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_latest_room(request):
    try:
        robot_telemetry = RobotTelemetry.objects.order_by('-id').first()
        serializer = RobotTelemetryLastRobotRoomOpeningSerializer(robot_telemetry, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Room status updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in room_status_detail: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_battery_status(request):
    """
    Create or update the latest BatteryStatus record.
    If a record exists, updates it; otherwise, creates a new one.
    """
    try:
        instance = BatteryStatus.objects.order_by('-id').first()
        if instance:
            # Update existing record
            serializer = BatteryStatusSerializer(instance, data=request.data, partial=True)
            action_message = "BatteryStatus updated"
        else:
            # Create new record
            serializer = BatteryStatusSerializer(data=request.data)
            action_message = "BatteryStatus created"
        if serializer.is_valid():
            serializer.save()
            return Response({
                    "status": "success",
                    "message": action_message,
                    "data": serializer.data,
                }, status=status.HTTP_200_OK,)
        return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST,)
    except Exception as e:
        logger.exception(f"BatteryStatus error: {e}")
        return Response({
                "status": "error",
                "message": "Internal server error",
                "data": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET','POST'])
@permission_classes([AllowAny])
def map_management_list_getsert(request):
    try:
        if request.method == 'GET':
            maps = MapManagement.objects.all().order_by('-created_at')
            serializer = MapManagementSerializer(maps, many=True, context={"request": request})
            return Response({
                "status": "success",
                "message": "Maps fetched successfully.",
                "data": serializer.data
            })

        elif request.method == 'POST':
            serializer = MapManagementSerializer(data=request.data)
            MapManagement.objects.filter(is_active=True).update(is_active=False)
            if serializer.is_valid():
                instance= serializer.save(is_active=True)
                # stcm_file = request.FILES.get("robot_map_file")

                # if stcm_file:
                #     ok = save_stcm_image_to_db(stcm_file, instance)
                #     if not ok:
                #         logger.warning("STCM file processing failed.")
                return Response({
                    "status": "success",
                    "message": "Map created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in map_management_list_create: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_map(request):
    try:
        active_map = MapManagement.objects.filter(is_active=True).first()
        if not active_map:
            return Response({
                "status": "error",
                "message": "No active map found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = MapManagementSerializer(active_map, context={"request": request})
        return Response({
            "status": "success",
            "message": "Active map fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in get_active_map: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def activate_map(request, map_id):
    try:

        robot_telemetry = RobotTelemetry.objects.order_by('-id').first()
        if robot_telemetry.robot_in_dock == False:
            return Response({
                "status": "error",
                "message": "Cannot change map while robot not in dock."
            }, status=status.HTTP_400_BAD_REQUEST)

        map_to_activate = get_object_or_404(MapManagement, pk=map_id)

        # Deactivate all maps
        MapManagement.objects.filter(is_active=True).update(is_active=False)

        # Activate the selected map
        map_to_activate.is_active = True
        map_to_activate.save()

        serializer = MapManagementSerializer(map_to_activate, context={"request": request})
        return Response({
            "status": "success",
            "message": f"Map '{map_to_activate.map_name}' activated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in activate_map: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_map(request, pk):
    try:
        map_instance = get_object_or_404(MapManagement, pk=pk)
        map_name = map_instance.map_name
        map_instance.delete()
        return Response({
            "status": "success",
            "message": f"Map '{map_name}' deleted successfully."
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"Exception in delete_map: {e}")
        return Response({
            "status": "error",
            "message": "Internal server error.",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# def save_stcm_image_to_db(stcm_file, instance):
#     print("🔵 [save_stcm_image_to_db] called")
#     logger.debug("save_stcm_image_to_db triggered")
#     """
#     Upload STCM file, convert to PNG, and save into RobotTelemetry.robot_image_file.
#     Falls back to auto-detected grid size if header and payload mismatch.
#     """
#     try:
#         if not stcm_file:
#             return Response(
#                 {"status": "error", "message": "STCM file is required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Read file content
#         data = stcm_file.read()

#         # Parse header (first 20 bytes)
#         try:
#             height, width, origin_x, origin_y, resolution = struct.unpack(
#                 "<iiiii", data[:20]
#             )
#         except Exception:
#             return Response(
#                 {"status": "error", "message": "Invalid STCM file format."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         logger.debug(
#             f"STCM header -> height={height}, width={width}, "
#             f"origin_x={origin_x}, origin_y={origin_y}, resolution={resolution}"
#         )

#         # Extract occupancy grid data
#         grid_data = data[20:]
#         payload_size = len(grid_data)
#         expected_size = height * width

#         logger.debug(f"Payload bytes={payload_size}, expected={expected_size}")

#         grid = None
#         # Case 1: payload matches header -> safe reshape
#         if payload_size == expected_size:
#             print("case 1")
#             grid = np.frombuffer(grid_data, dtype=np.int8).reshape((height, width))
#             logger.debug("Grid parsed using header values.")
#         else:
#             print("case 2")
#             # Case 2: fallback -> auto-detect square grid
#             side = int(np.sqrt(payload_size))
#             usable = side * side
#             grid = np.frombuffer(grid_data[:usable], dtype=np.int8).reshape((side, side))
#             logger.warning(
#                 f"Header mismatch (expected {expected_size}, got {payload_size}). "
#                 f"Falling back to {side}x{side} grid."
#             )

#         # Map values to RGB
#         img_array = np.zeros((grid.shape[0], grid.shape[1], 3), dtype=np.uint8)
#         img_array[grid == 0] = [255, 255, 255]   # free = white
#         img_array[grid == 1] = [0, 0, 0]         # occupied = black
#         img_array[grid == -1] = [128, 128, 128]  # unknown = gray

#         # Create PNG image
#         img = Image.fromarray(img_array)

#         # Save into memory
#         buffer = BytesIO()
#         img.save(buffer, format="PNG")
#         buffer.seek(0)

#         file_name = f"map_{instance.pk}.png"
#         instance.robot_map_image_file.save(file_name, ContentFile(buffer.read()), save=True)

#         # Verify
#         if instance.robot_map_image_file and instance.robot_map_image_file:
#             print(f"Image saved successfully: {instance.robot_map_image_file}")
#             logger.debug(f"Image saved successfully: {instance.robot_map_image_file}")
#         else:
#             print("Image save failed!")
#             logger.debug("Image save failed for instance ID=%s", instance.pk)

#         logger.debug(f"STCM image saved successfully for MapManagement id={instance.pk}")
#         print(f"Image saved successfully for instance ID={instance.pk}")
#         return True

#     except Exception as e:
#         logger.exception(f"Failed to process STCM file: {e}")
#         print(f"Exception in save_stcm_image_to_db: {e}")
#         raise ValueError(f"Failed to process STCM file: {e}")

# ---- JointHeat ----
@api_view(["GET", "PUT"])
@permission_classes([AllowAny])
def create_or_update_joint_heat(request):
    try:
        instance = get_single_instance(JointHeat)

        if request.method == "GET":
            serializer = JointHeatSerializer(instance)
            return Response({"status": "success", "data": serializer.data})

        elif request.method == "PUT":
            serializer = JointHeatSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "joint_heat_group",
                    {
                        "type": "joint_heat_message",
                        "payload": {
                            "j1": obj.j1,
                            "j2": obj.j2,
                            "j3": obj.j3,
                            "j4": obj.j4,
                            "j5": obj.j5,
                            "j6": obj.j6,
                        }
                    },
                )

                return Response({"status": "success", "message": "Updated", "data": serializer.data})
            return Response({"status": "error", "errors": serializer.errors}, status=400)

    except Exception as e:
        logger.exception(f"JointHeat error: {e}")
        return Response({"status": "error", "message": str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_joint_heat(request):
    try:
        instance = JointHeat.objects.order_by('id').first()
        if not instance:
            return Response(
                {"status": "error", "message": "No JointHeat found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = JointHeatSerializer(instance)
        return Response(
            {
                "status": "success",
                "message": "Latest JointHeat fetched",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"ArmStatus fetch error: {e}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
# ---- Slot Reached Position ----
@api_view(["POST"])
@permission_classes([AllowAny])
def slot_reached_pos(request):
    try:
        room = request.data.get("room")
        bed = request.data.get("bed")
        robot_telemetry = RobotTelemetry.objects.order_by('id').first()
        if robot_telemetry:
            robot_telemetry.latest_room_reached = room
            robot_telemetry.latest_bed_reached = bed
            robot_telemetry.save(update_fields=["latest_room_reached", "latest_bed_reached"])

        room = RoomDataModel.objects.get(room_name=room)
        bed = BedDataModel.objects.get(bed_name=bed)
        slot = SlotDataModel.objects.get(room_name=room.pk, bed_name=bed.pk)

        patient = Patient.objects.filter(slot_assigned=slot.pk, is_active=True).first()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "slot_group",
            {
                "type": "slot_message",
                "payload": {
                    "id": patient.pk,
                    "patient_id": patient.patient_id,
                    "name": patient.name,
                    "gender": patient.gender,
                    "age": patient.age,
                    "slot": {
                        "room": room.room_name,
                        "bed": bed.bed_name,
                        "x": slot.x,
                        "y": slot.y,
                        "yaw": slot.yaw,
                    }
                }
            },
        )
        # ✅ return success response
        return Response({"status": "success", "message": "Slot position broadcasted."})

    except Exception as e:
        logger.exception(f"JointHeat error: {e}")
        return Response({"status": "error", "message": str(e)}, status=500)