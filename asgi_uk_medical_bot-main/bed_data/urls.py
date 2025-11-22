from django.urls import path
from .views import create_or_update_room, view_all_rooms, create_or_update_bed, view_all_bed, \
            create_slot, view_all_slot, soft_delete_slot, view_active_slot, create_slot_position,create_room_position_view, \
            create_room_position_activate, create_room_entry_point, create_room_exit_point

urlpatterns = [

    path('room/create/', create_or_update_room, name='create-room'),
    path('room/all/', view_all_rooms, name='room all'),

    path('bed/create/', create_or_update_bed, name='create-bed'),
    path('bed/all/', view_all_bed, name='bed all'),

    path('slot/create/', create_slot, name='create-slot'),
    path('slot/all/', view_all_slot, name='slot all'),
    path('slot/active/', view_active_slot, name='active slots'),
    path('slot/delete/<int:slot_id>/', soft_delete_slot, name='soft delete slot'),

    path('slot/position/create/', create_slot_position, name='create-slot-position'),

    # path('room/position/create/', create_room_position, name='create-room-position'),
    path('room/position/view/', create_room_position_view, name='create-room-position-view'),
    path('room/position/activate/<int:pk>/', create_room_position_activate, name='create-room-position-activate'),

    path('room/entry-point/position/create/', create_room_entry_point, name='create-room-entry-point'),
    path('room/exit-point/position/create/', create_room_exit_point, name='create-room-exit-point'),
    
]