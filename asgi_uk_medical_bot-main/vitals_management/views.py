from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging
from .models import Bp2CheckMeModel
from .serializers import Bp2CheckMeSerializer
from  privilagecontroller.views import hasFeatureAccess
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.pagination import PageNumberPagination

class ApparatusPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

logger = logging.getLogger(__name__)

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def upsert_bp2_checkme(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'bp2_checkme_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        pk = request.data.get('pk')
        if pk:
            try:
                instance = Bp2CheckMeModel.objects.get(id=pk)
            except Bp2CheckMeModel.DoesNotExist:
                return Response({'status': 'error', 'message': 'Record not found.', 'data': None},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = Bp2CheckMeSerializer(instance, data=request.data, partial=True)
            operation = "updated"
        else:
            serializer = Bp2CheckMeSerializer(data=request.data, partial=True)
            operation = "created"

        if serializer.is_valid():
            serializer.save(
                updated_by=request.user if pk else None,
                created_by=request.user if not pk else instance.created_by
            )
            return Response({
                'status': 'success',
                'message': f'BP2CheckMe record {operation} successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK if pk else status.HTTP_201_CREATED)

        errors = {field: messages[0] for field, messages in serializer.errors.items()}
        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            "error": {"details": errors}
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in upsert_bp2checkme: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_bp2_checkme(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'bp2_checkme_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        records = Bp2CheckMeModel.objects.all().order_by('-created_at')
        paginator = ApparatusPagination()
        paginated_patients = paginator.paginate_queryset(records, request)
        serializer = Bp2CheckMeSerializer(paginated_patients, many=True, context={'request': request})

        return paginator.get_paginated_response({
            'status': 'success',
            'message': 'All BP2CheckMe records retrieved successfully',
            'data': serializer.data
        })

    except Exception as e:
        logger.exception(f"Exception in list_all_bp2checkme: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_bp2checkme_active(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'bp2_checkme_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        pk = request.data.get('pk')
        if not pk:
            return Response({'status': 'error', 'message': 'Primary key (pk) is required.', 'data': None},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = Bp2CheckMeModel.objects.get(id=pk)
        except Bp2CheckMeModel.DoesNotExist:
            return Response({'status': 'error', 'message': 'Record not found.', 'data': None},
                            status=status.HTTP_404_NOT_FOUND)

        # Toggle
        instance.is_active = not instance.is_active
        instance.save(update_fields=['is_active'])

        return Response({
            'status': 'success',
            'message': f"Record {'activated' if instance.is_active else 'deactivated'}.",
            'data': {'id': instance.id, 'is_active': instance.is_active}
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in toggle_bp2checkme_active: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def robot_upsert_bp2_checkme(request):
    try:
        patient = request.data.get('patient')
        if not patient:
            return Response(
                {'status': 'error', 'message': 'Require patient id.', 'data': None},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = Bp2CheckMeSerializer(data=request.data, partial=True)
        operation = "created"

        if serializer.is_valid():
            instance = serializer.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "apparatus_value_group",
                {
                    "type": "apparatus_value_message",
                    "payload": {
                        "sys": instance.sys,
                        'dia': instance.dia,
                        'map': instance.map,
                        'pulse_rate_note': instance.pulse_rate_note,
                    }
                }
            )

            return Response({
                'status': 'success',
                'message': f'BP2CheckMe record {operation} successfully.',
                'data': None
            }, status=status.HTTP_201_CREATED)

        errors = {field: messages[0] for field, messages in serializer.errors.items()}
        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            "error": {"details": errors}
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in upsert_bp2checkme: {e}")
        return Response(
            {'status': 'error', 'message': 'Internal server error.', 'data': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )