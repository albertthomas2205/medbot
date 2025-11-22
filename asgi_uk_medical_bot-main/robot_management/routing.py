from django.urls import re_path
from . import consumers

# def lazy_stream_view(scope):
#     from .views import streamVoiceOutput
#     return streamVoiceOutput(scope)

websocket_urlpatterns = [
    
    # re_path(r'ws/socket-server/$', lazy_stream_view),
    re_path(r'ws/socket-server/slot/', consumers.SlotPatientReturn.as_asgi()),
    re_path(r'ws/socket-server/help/', consumers.HelpReturn.as_asgi()),
    re_path(r'ws/socket-server/notification/', consumers.Notification.as_asgi()),
    re_path(r'ws/socket-server/apparatus-value/', consumers.ApparatusValue.as_asgi()),
    re_path(r'ws/socket-server/scheduler-data/', consumers.SchedulerValue.as_asgi()),
    re_path(r'ws/socket-server/emergency-status/', consumers.EmergencyValue.as_asgi()),
    re_path(r'ws/socket-server/robot-distance-accuracy/', consumers.RobotEntryExitAccDis.as_asgi()),
    re_path(r'ws/socket-server/arm-endpose-value/', consumers.ArmEndposeValue.as_asgi()),
    re_path(r'ws/socket-server/joint-velocity-value/', consumers.JointVelocityValue.as_asgi()),
    re_path(r'ws/socket-server/joint-effort-value/', consumers.JointEffortValue.as_asgi()),
    re_path(r'ws/socket-server/joint-position-value/', consumers.JointPositionValue.as_asgi()),
    re_path(r'ws/socket-server/refresh-arm-data-value/', consumers.RefreshArmDataValue.as_asgi()),
    re_path(r'ws/socket-server/refresh-joint-data-value/', consumers.RefreshJointDataValue.as_asgi()),
    re_path(r'ws/socket-server/joint-heat-value/', consumers.JointHeatConsumer.as_asgi()),

]