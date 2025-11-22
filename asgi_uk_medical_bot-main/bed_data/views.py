from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging
from .models import RoomDataModel, BedDataModel, SlotDataModel, RoomPositionModel
from privilagecontroller.views import hasFeatureAccess
from .serializer import RoomDataSerializer, BedDataSerializer, SlotDataModelSerializer, RoomPositionModelSerializer
from django.db import IntegrityError
from django.db import connection
from django.db.models import Max
from django.db.models.functions import Cast, Substr
from django.db import models

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_room(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=403)

        if not hasFeatureAccess(request.user, 'room_data_handling_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=403)

        try:
            rooms_to_add = int(request.data.get('count'))
            if rooms_to_add < 1:
                raise ValueError
        except (TypeError, ValueError):
            return Response({'status': 'error', 'message': 'Invalid count provided.', 'data': None}, status=400)

        # find last created index (globally)
        last_index = get_last_index(RoomDataModel, "room")

        new_rooms = []
        for i in range(last_index + 1, last_index + rooms_to_add + 1):
            room_name = f"room_{i}"
            new_room = RoomDataModel.objects.create(
                room_name=room_name,
                created_by=request.user,
                is_active=True
            )
            new_rooms.append(RoomDataSerializer(new_room).data)

        return Response({
            'status': 'success',
            'message': f'{rooms_to_add} room(s) created successfully.',
            'data': new_rooms
        }, status=201)

    except Exception as e:
        logger.exception(f"Exception in room_data_handling_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=500)

def get_next_room_number():
    last_room = RoomDataModel.objects.aggregate(
        max_num=Max(
            models.functions.Cast(
                models.functions.Substr("room_name", 6),
                output_field=models.IntegerField()
            )
        )
    )["max_num"] or 0
    return last_room + 1

def get_last_index(model, prefix):
    """
    Returns the highest number already used for given model's prefix (room_ / bed_).
    """
    last_num = model.objects.annotate(
        num=Cast(Substr(f"{prefix}_name", len(prefix) + 2), models.IntegerField())
    ).aggregate(max_num=Max("num"))["max_num"] or 0
    return last_num

# READ All Rooms
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_rooms(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'room_data_handling_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        rooms = RoomDataModel.objects.all()
        serializer = RoomDataSerializer(rooms, many=True)
        return Response({'status': 'success', 'message': 'Rooms fetched successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in room_data_handling_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_bed(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=403)

        if not hasFeatureAccess(request.user, 'room_data_handling_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=403)

        try:
            beds_to_add = int(request.data.get('count'))
            if beds_to_add < 1:
                raise ValueError
        except (TypeError, ValueError):
            return Response({'status': 'error', 'message': 'Invalid count provided.', 'data': None}, status=400)

        # find last created index (globally)
        last_index = get_last_index(BedDataModel, "bed")

        new_beds = []
        for i in range(last_index + 1, last_index + beds_to_add + 1):
            bed_name = f"bed_{i}"
            new_bed = BedDataModel.objects.create(
                bed_name=bed_name,
                created_by=request.user,
                is_active=True
            )
            new_beds.append(BedDataSerializer(new_bed).data)

        return Response({
            'status': 'success',
            'message': f'{beds_to_add} bed(s) created successfully.',
            'data': new_beds
        }, status=201)

    except Exception as e:
        logger.exception(f"Exception in bed_data_handling_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=500)

# READ All Rooms
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_bed(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'room_data_handling_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        rooms = BedDataModel.objects.all()
        serializer = BedDataSerializer(rooms, many=True)
        return Response({'status': 'success', 'message': 'Rooms fetched successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in room_data_handling_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_slot(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'slot_management_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        room_id = request.data.get("room_name_id")
        bed_id = request.data.get("bed_name_id")
        x = request.data.get("x") or 0
        y = request.data.get("y") or 0
        yaw = request.data.get("yaw") or 0

        if not room_id or not bed_id:
            return Response({'status': 'error', 'message': 'Room and Bed are required.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        exist = SlotDataModel.objects.filter(room_name=room_id, bed_name=bed_id).exists()
        if exist:
            return Response({'status': 'error', 'message': 'Slot already exist (activate if inactive).', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slot = SlotDataModel.objects.create(
                room_name_id=room_id,
                bed_name_id=bed_id,
                x=x,
                y=y,
                yaw=yaw,
                created_by=request.user
            )
            return Response({'status': 'success', 'message': 'Slot created successfully.', 'data': slot.id}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({'status': 'error', 'message': 'This room-bed slot already exists.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in slot_management_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# READ All Rooms
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_slot(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'slot_management_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        slots = SlotDataModel.objects.all().order_by('-created_at')
        serializer = SlotDataModelSerializer(slots, many=True)
        slots_count = SlotDataModel.objects.all().count()
        return Response({'status': 'success', 'message': 'Slots fetched successfully.', 'data': serializer.data, 'count': slots_count}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in slot_management_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_active_slot(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'slot_management_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        rooms = SlotDataModel.objects.filter(is_active = True)
        serializer = SlotDataModelSerializer(rooms, many=True)
        return Response({'status': 'success', 'message': 'Slots fetched successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in slot_management_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def soft_delete_slot(request, slot_id):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'slot_management_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        slot_instance = SlotDataModel.objects.filter(id=slot_id).first()
        if not slot_instance:
            return Response({
                'status': 'error',
                'message': 'Slot not found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        slot_instance.is_active = not slot_instance.is_active
        # updated_instance = slot_instance.save()
        if slot_id:
            slot_instance.updated_by = request.user
        else:
            slot_instance.created_by = request.user
        slot_instance.save() 
        action = 'activated' if slot_instance.is_active else 'deactivated'
        return Response({
            'status': 'success',
            'message': f"Slot {action} successfully.",
            'data': None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in slot_management_crud: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def create_slot_position(request):
    try:
        # if request.user.role not in ['admin', 'nurse']:
        #     return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        # if not hasFeatureAccess(request.user, 'slot_management_crud'):
        #     return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        slot_id = request.data.get("slot_id")
        x = request.data.get("x")
        y = request.data.get("y")
        yaw = request.data.get("yaw")

        if not slot_id or not x or not y or not yaw:
            return Response({'status': 'error', 'message': 'Slot id and positions are required.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        exist = SlotDataModel.objects.filter(id=slot_id).exists()
        if not exist:
            return Response({'status': 'error', 'message': 'Slot does not exist.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slot = SlotDataModel.objects.filter(id=slot_id).update(
                x=x,
                y=y,
                yaw=yaw,
                # updated_by=request.user
            )
            return Response({'status': 'success', 'message': 'Slot created successfully.', 'data': None}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({'status': 'error', 'message': 'Something went wrong.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        import traceback
        logger.exception(f"Exception in slot_management_crud: {e}")
        error = traceback.format_exc()
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# @api_view(['POST'])
# def create_room_position(request):
#     try:
#         if request.user.role not in ['admin', 'nurse']:
#             return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

#         if not hasFeatureAccess(request.user, 'slot_management_crud'):
#             return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

#         room_pos_id = request.data.get("room_pos_id")

#         # if not slot_id or not x or not y or not yaw:
#         #     return Response({'status': 'error', 'message': 'Slot id and positions are required.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

#         try:

#             if room_pos_id:
#                 instance = RoomPositionModel.objects.filter(id=room_pos_id).first()
#                 if not instance:
#                     return Response(
#                         {'status': 'error', 'message': 'Room position not found.', 'data': None},
#                         status=status.HTTP_404_NOT_FOUND
#                     )
#                 serializer = RoomPositionModelSerializer(instance, data=request.data, partial=True)
#             else:
#                 serializer = RoomPositionModelSerializer(data=request.data)

#             if serializer.is_valid():
#                 obj = serializer.save(created_by=request.user, updated_by=request.user, is_active=True)
#                 return Response(
#                     {'status': 'success', 'message': 'Room position saved successfully.', 'data': RoomPositionModelSerializer(obj).data},
#                     status=status.HTTP_201_CREATED
#                 )
#             else:
#                 return Response(
#                     {'status': 'error', 'message': 'Validation failed.', 'data': serializer.errors},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         except IntegrityError as e:
#             if 'unique_room_slot' in str(e):
#                 return Response(
#                     {
#                         'status': 'error',
#                         'message': 'A room position for this room already exists.',
#                         'data': None
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             return Response(
#                 {
#                     'status': 'error',
#                     'message': 'Database integrity error.',
#                     'data': str(e)  # optional, remove in production
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#     except Exception as e:
#         logger.exception(f"Exception in slot_management_crud: {e}")
#         return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def create_room_position_view(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'slot_management_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)
        
        all_rooms = RoomDataModel.objects.all()
        existing_rooms = RoomPositionModel.objects.values_list('room_name', flat=True)

        new_positions = []
        for room in all_rooms:
            if room.id not in existing_rooms:
                new_positions.append(
                    RoomPositionModel(
                        room_name = room,
                        created_by=request.user,
                        updated_by=request.user
                    )
                )
        
        if new_positions:
            RoomPositionModel.objects.bulk_create(new_positions)

        rooms_positions = RoomPositionModel.objects.all().order_by('-created_at')
        serializer = RoomPositionModelSerializer(rooms_positions, many=True)

        return Response({'status': 'success', 'message': 'Room position data fetched successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in slot_management_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def create_room_position_activate(request, pk):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'slot_management_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        slot_instance = RoomPositionModel.objects.filter(id=pk).first()
        if not slot_instance:
            return Response({
                'status': 'error',
                'message': 'Slot not found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        slot_instance.is_active = not slot_instance.is_active
        # updated_instance = slot_instance.save()
        slot_instance.updated_by = request.user
        slot_instance.save() 
        action = 'activated' if slot_instance.is_active else 'deactivated'
        return Response({
            'status': 'success',
            'message': f"Room position {action} successfully.",
            'data': None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in slot_management_crud: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def create_room_entry_point(request):
    try:
        # if request.user.role not in ['admin', 'nurse']:
        #     return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        # if not hasFeatureAccess(request.user, 'slot_management_crud'):
        #     return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        room_pos_id = request.data.get("room_pos_id")
        x = request.data.get("x")
        y = request.data.get("y")
        yaw = request.data.get("yaw")

        if not room_pos_id or not x or not y or not yaw:
            return Response({'status': 'error', 'message': 'Room position id and positions are required.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        exist = RoomPositionModel.objects.filter(id=room_pos_id).exists()
        if not exist:
            return Response({'status': 'error', 'message': 'Room does not exist.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slot = RoomPositionModel.objects.filter(id=room_pos_id).update(
                entry_point_x=x,
                entry_point_y=y,
                entry_point_yaw=yaw,
                # updated_by=request.user
            )
            return Response({'status': 'success', 'message': 'Room entry position created successfully.', 'data': None}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': 'Something went wrong.',
                    'data': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.exception(f"Exception in slot_management_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def create_room_exit_point(request):
    try:
        # if request.user.role not in ['admin', 'nurse']:
        #     return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        # if not hasFeatureAccess(request.user, 'slot_management_crud'):
        #     return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        room_pos_id = request.data.get("room_pos_id")
        x = request.data.get("x")
        y = request.data.get("y")
        yaw = request.data.get("yaw")

        if not room_pos_id or not x or not y or not yaw:
            return Response({'status': 'error', 'message': 'Room position id and positions are required.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        exist = RoomPositionModel.objects.filter(id=room_pos_id).exists()
        if not exist:
            return Response({'status': 'error', 'message': 'Room does not exist.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slot = RoomPositionModel.objects.filter(id=room_pos_id).update(
                exit_point_x=x,
                exit_point_y=y,
                exit_point_yaw=yaw,
                # updated_by=request.user
            )
            return Response({'status': 'success', 'message': 'Room exit position created successfully.', 'data': None}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': 'Something went wrong.',
                    'data': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.exception(f"Exception in slot_management_crud: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)