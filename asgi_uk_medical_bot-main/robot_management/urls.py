from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
               
    path('create-robot-telemetry/', create_or_update_robot_telemetry, name='get the room_cord'),

    path('get-patient-data/<int:patient_id>/', get_patient_data, name='get the room_cord'),
    path('get-room_entry_cord/<str:room>/', get_room_entry_cord, name='get the room_cord'),
    path('get-room_exit_cord/<str:room>/', get_room_exit_cord, name='get the room_cord'),
    path('get-slot_cord/<str:room>/<str:bed>/', get_slot_cord, name='get the slot cord'),

    path('save-help-data/', save_help, name='save help data'),
    path('respond-help/<int:alert_id>/<int:rsp>/', respond_alert, name='respond to alert'),
    path("alerts/", view_all_alerts, name="view_all_alerts"),
    path("alerts/<int:pk>/update-reason/", update_alert_reason, name="update alert reason"),
    path("active/alerts/", view_active_alerts, name="view active alerts"),

    path("fetch-latest-slot/", fetch_latest_slot, name="fetch latest slot"),

    path("all-robot-telemetry/", robot_telemetry_all, name="fetch all robot telemetry"),

    # path("save-map-telemetry/", save_stcm_image_to_db, name="save_stcm_to_db url"),

    path("arm-endpose/", arm_endpose, name="arm_endpose url"),
    path("joint-velocity/", joint_velocity, name="joint_velocity url"),
    path("joint-effort/", joint_effort, name="joint_effort url"),
    path("joint-position/", joint_position, name="joint_position url"),

    path("create-update-arm-status/", create_or_update_arm_status, name="create or update arm status"),
    path("get-arm-status/", get_arm_status, name="get arm status"),

    path("create-update-joint-status/", create_or_update_joint_status, name="create or update joint status"),
    path("get-joint-status/", get_joint_status, name="get joint status"),

    path("getup/robot/status/", getup_robot_status, name="get or update robot status"),
    path("getup/robot/volume/", getup_volume_status, name="get or update robot volume"),
    path("getup/robot/robot_emergency/", getup_robot_emergency_status, name="get or update robot emergency"),

    path("save/robot/stcm_map/", save_stcm_map, name="save stcm map"),

    path("failed-schedules/", failed_scheduled_list_create, name="failed_scheduled_list_create"),
    path("failed-schedules/<int:pk>/", failed_scheduled_mark_respond, name="failed_scheduled_mark_respond"),

    path("robot/latest/room/", update_latest_room, name="update_latest_room"),

    path("upsert-battery/status/", create_or_update_battery_status, name="upsert battery status"),

    # Map Management APIs
    path("maps/getsert/", map_management_list_getsert, name="map_management_list_create and insert"),
    path("map/active/", get_active_map, name="get_active_map"),
    path("maps/activate-map/<int:map_id>/", activate_map, name="activate_map"),
    path("maps/<int:pk>/delete/", delete_map, name="delete map"),

    path("create-update-joint-heat/", create_or_update_joint_heat, name="create or update joint heat"),
    path("get-joint-heat/", get_joint_heat, name="get joint heat"),

    path("transfer-slot-reached-pos/", slot_reached_pos, name="transfer slot reached position"),

]