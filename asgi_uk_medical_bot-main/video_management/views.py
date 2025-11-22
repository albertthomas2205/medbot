from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import VideoManagementModel
from .serializers import VideoManagementModelSerializer
import logging
from privilagecontroller.views import hasFeatureAccess
logger = logging.getLogger(__name__)
from django.utils.crypto import get_random_string
from django.db import transaction

# @api_view(['POST', 'PUT'])
# @permission_classes([IsAuthenticated])
# def update_video(request):
#     try:
#         if request.user.role not in ['admin', 'nurse']:
#             return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
#                             status=status.HTTP_403_FORBIDDEN)

#         if not hasFeatureAccess(request.user, 'video_management_crud'):
#             return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
#                             status=status.HTTP_403_FORBIDDEN)

#         pk = request.data.get('pk')
#         if pk:
#             try:
#                 instance = VideoManagementModel.objects.get(id=pk)
#             except VideoManagementModel.DoesNotExist:
#                 return Response({'status': 'error', 'message': 'Video not found.', 'data': None},
#                                 status=status.HTTP_404_NOT_FOUND)

#             serializer = VideoManagementModelSerializer(instance, data=request.data, partial=True)
#             operation = "updated"
#         else:
#             serializer = VideoManagementModelSerializer(data=request.data, partial=True)
#             operation = "created"

#         if serializer.is_valid():
#             serializer.save(
#                 updated_by=request.user if pk else None,
#                 created_by=request.user if not pk else instance.created_by
#             )
#             return Response({
#                 'status': 'success',
#                 'message': f'Video {operation} successfully.',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK if pk else status.HTTP_201_CREATED)

#         errors = {field: messages[0] for field, messages in serializer.errors.items()}
#         return Response({
#             'status': 'error',
#             'message': 'Validation failed.',
#             "error": {"details": errors}
#         }, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         logger.exception(f"Exception in update_video: {e}")
#         return Response({
#             'status': 'error',
#             'message': 'Internal server error.',
#             'data': None
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def update_video(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'video_management_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        pk = request.data.get('pk')
        file = request.FILES.get('video_image_file')

        # --- Determine file type ---
        is_image = None
        if file:
            ext = file.name.split('.')[-1].lower()
            image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
            video_exts = {'mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'webm'}
            
            if ext in image_exts:
                is_image = True
            elif ext in video_exts:
                is_image = False
            else:
                return Response({
                    'status': 'error',
                    'message': f'Unsupported file type: .{ext}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

        # --- Update or create instance ---
        if pk:
            try:
                instance = VideoManagementModel.objects.get(id=pk)
            except VideoManagementModel.DoesNotExist:
                return Response({'status': 'error', 'message': 'Video not found.', 'data': None},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = VideoManagementModelSerializer(instance, data=request.data, partial=True)
            operation = "updated"
        else:
            serializer = VideoManagementModelSerializer(data=request.data, partial=True)
            operation = "created"

        if serializer.is_valid():
            obj = serializer.save(
                updated_by=request.user if pk else None,
                created_by=request.user if not pk else instance.created_by
            )

            # --- Update is_image flag only if file uploaded ---
            if is_image is not None:
                obj.is_image = is_image
                obj.save(update_fields=['is_image'])

            return Response({
                'status': 'success',
                'message': f'Video {operation} successfully.',
                'data': VideoManagementModelSerializer(obj).data
            }, status=status.HTTP_200_OK if pk else status.HTTP_201_CREATED)

        # Validation errors
        errors = {field: messages[0] for field, messages in serializer.errors.items()}
        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            "error": {"details": errors}
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in update_video: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_video(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'video_management_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        videos = VideoManagementModel.objects.all().order_by('id')
        serializer = VideoManagementModelSerializer(videos, many=True, context={'request': request})

        return Response({
            'status': 'success',
            'message': 'All videos retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_video: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def view_active_video(request):
    try:
        videos = VideoManagementModel.objects.filter(is_active=True).order_by('id')
        serializer = VideoManagementModelSerializer(videos, many=True, context={'request': request})

        return Response({
            'status': 'success',
            'message': 'All active videos retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_active_video: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_video(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'video_management_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None},
                            status=status.HTTP_403_FORBIDDEN)

        pk = request.data.get('pk')
        if not pk:
            return Response({'status': 'error', 'message': 'Primary key (pk) is required.', 'data': None},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = VideoManagementModel.objects.get(id=pk)
        except VideoManagementModel.DoesNotExist:
            return Response({'status': 'error', 'message': 'Video not found.', 'data': None},
                            status=status.HTTP_404_NOT_FOUND)

        instance.is_active = not instance.is_active
        instance.save(update_fields=['is_active'])

        message = "Video activated." if instance.is_active else "Video deactivated."
        return Response({'status': 'success', 'message': message, 'data': None},
                        status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in delete_video: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def swap_video_order(request):
    try:
        id1 = request.data.get("pk1")
        id2 = request.data.get("pk2")

        if not id1 or not id2:
            return Response({"status": "error", "message": "Both pk1 and pk2 are required.", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            obj1 = VideoManagementModel.objects.get(pk=id1)
            obj2 = VideoManagementModel.objects.get(pk=id2)
        except VideoManagementModel.DoesNotExist:
            return Response({"status": "error", "message": "One or both objects not found.", "data": None},
                            status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            orig1 = {
                "video_name": obj1.video_name,
                "video_image_url": obj1.video_image_url,
                "video_image_file": obj1.video_image_file,
                "is_active": obj1.is_active,
                "created_by": obj1.created_by,
                "updated_by": obj1.updated_by,
            }
            orig2 = {
                "video_name": obj2.video_name,
                "video_image_url": obj2.video_image_url,
                "video_image_file": obj2.video_image_file,
                "is_active": obj2.is_active,
                "created_by": obj2.created_by,
                "updated_by": obj2.updated_by,
            }

            temp_name = f"__temp__{get_random_string(8)}"
            obj1.video_name = temp_name
            obj1.save(update_fields=["video_name"])

            obj1.video_name = orig2["video_name"]
            obj1.video_image_url = orig2["video_image_url"]
            obj1.video_image_file = orig2["video_image_file"]
            obj1.is_active = orig2["is_active"]
            obj1.created_by = orig2["created_by"]
            obj1.updated_by = orig2["updated_by"]

            obj2.video_name = orig1["video_name"]
            obj2.video_image_url = orig1["video_image_url"]
            obj2.video_image_file = orig1["video_image_file"]
            obj2.is_active = orig1["is_active"]
            obj2.created_by = orig1["created_by"]
            obj2.updated_by = orig1["updated_by"]

            obj1.save()
            obj2.save()

        return Response({
            "status": "success",
            "message": f"Swapped all data between videos {id1} and {id2}",
            "data": {
                "video1": VideoManagementModelSerializer(obj1).data,
                "video2": VideoManagementModelSerializer(obj2).data
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in swap_video_order: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)