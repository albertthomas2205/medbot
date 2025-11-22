from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
import json


# # ---------------------- Slot Patient Return ----------------------
# class SlotPatientReturn(AsyncWebsocketConsumer):
#     group_name = "slot_group"

#     async def connect(self):
#         await self.accept()
#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.send(text_data=json.dumps({
#             "type": "connection_established",
#             "message": "you are connected to slot"
#         }))

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)

#     # async def receive(self, text_data):
#     #     try:
#     #         data = json.loads(text_data)
#     #         if not text_data:  # empty frame
#     #             print("[WS] Empty message received, ignoring")
#     #             return
#     #         room = data.get("room")
#     #         bed = data.get("bed")
#     #         if room is None and bed is None:
#     #             print("[WS] Skipping message — no room/bed provided")
#     #             return

#     #         # Save telemetry
#     #         await self.save_telemetry(data)

#     #         # Get patient info
#     #         patient_data = await self.get_patient_by_room_bed(room, bed)
#     #         if not patient_data:
#     #             patient_data = {"error": "No active patient found"}

#     #         # Send only to slot group
#     #         await self.channel_layer.group_send(
#     #             self.group_name,
#     #             {
#     #                 "type": "slot_message",   # must match method name
#     #                 "payload": patient_data
#     #             }
#     #         )

#     #     except Exception as e:
#     #         print(f"[Server Error][SlotPatientReturn] {e}")
#     #         await self.close(code=1011)

#     async def slot_message(self, event):
#         payload = event.get("payload")
#         await self.send(text_data=json.dumps({"payload": payload}))

#     @database_sync_to_async
#     def save_telemetry(self, data):
#         from .models import RobotTelemetry
#         updates = {}
#         if data.get("room"):   # only update if not None/empty
#             updates["latest_room_reached"] = data["room"]
#         if data.get("bed"):
#             updates["latest_bed_reached"] = data["bed"]

#         if updates:  # update only if there are real values
#             telemetry, _ = RobotTelemetry.objects.update_or_create(
#                 pk=1,
#                 defaults=updates
#             )
#             return telemetry

#     @sync_to_async
#     def get_patient_by_room_bed(self, room_name, bed_name):
#         from bed_data.models import RoomDataModel, BedDataModel, SlotDataModel
#         from mainapp.models import Patient

#         try:
#             room = RoomDataModel.objects.get(room_name=room_name)
#             bed = BedDataModel.objects.get(bed_name=bed_name)
#             slot = SlotDataModel.objects.get(room_name=room.id, bed_name=bed.id)

#             patient = Patient.objects.filter(slot_assigned=slot.id, is_active=True).first()
#             if not patient:
#                 return None

#             return {
#                 "id": patient.pk,
#                 "patient_id": patient.patient_id,
#                 "name": patient.name,
#                 "gender": patient.gender,
#                 "age": patient.age,
#                 "slot": {
#                     "room": room.room_name,
#                     "bed": bed.bed_name,
#                     "x": slot.x,
#                     "y": slot.y,
#                     "yaw": slot.yaw,
#                 }
#             }
#         except Exception as e:
#             print(f"[DB Error][SlotPatientReturn] {e}")
#             return None



# ---------------------- Help Return ----------------------
class HelpReturn(AsyncWebsocketConsumer):
    group_name = "help_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to help"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            room = data.get("room")
            bed = data.get("bed")

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "help_message",
                    "payload": f"Immediate attention required at {bed} in {room}"
                }
            )
        except Exception as e:
            print(f"[Server Error][HelpReturn] {e}")
            await self.close(code=1011)

    async def help_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))


# # ---------------------- Notification ----------------------
class Notification(AsyncWebsocketConsumer):
    
    group_name = "notification_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to notifications"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            icon = data.get("icon")
            notification = data.get("notification")
            

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "notification_message",
                    "payload": {
                        "icon": icon,
                        "notification": notification
                    }
                }
            )
            
        
        except Exception as e:
            print(f"[Server Error][Notification] {e}")
            await self.close(code=1011)

    async def notification_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))



# ---------------------- Apparatus ----------------------
class ApparatusValue(AsyncWebsocketConsumer):
    group_name = "apparatus_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to apparatus value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            req_data = data.get("data")

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "apparatus_value_message",
                    "payload": {
                        "apparatus": req_data
                    }
                }
            )
        except Exception as e:
            print(f"[Server Error][apparatus] {e}")
            await self.close(code=1011)

    async def apparatus_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Scheduler ----------------------
class SchedulerValue(AsyncWebsocketConsumer):
    group_name = "scheduler_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to scheduler value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)



    async def scheduler_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps(payload))

# ---------------------- Emergency ----------------------
class EmergencyValue(AsyncWebsocketConsumer):
    group_name = "emergency_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to emergency value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def emergency_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Robot entry exit arm accuracy and distance ----------------------
class RobotEntryExitAccDis(AsyncWebsocketConsumer):
    group_name = "robot_entry_exit_acc_dis_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to emergency value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            req_data = data.get("data", text_data)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "robot_entry_exit_acc_dis_value_message",
                    "payload": data
                }
            )
        except Exception as e:
            print(f"[Server Error][robot_entry_exit_acc_dis] {e}")
            await self.close(code=1011)

    async def robot_entry_exit_acc_dis_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Arm Endpose ----------------------
class ArmEndposeValue(AsyncWebsocketConsumer):
    group_name = "arm_endpose_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to arm endpose value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

   
    async def arm_endpose_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Joint Velocity ----------------------
class JointVelocityValue(AsyncWebsocketConsumer):
    group_name = "joint_velocity_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to arm endpose value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def joint_velocity_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Joint Effort ----------------------
class JointEffortValue(AsyncWebsocketConsumer):
    group_name = "joint_effort_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to arm endpose value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def joint_effort_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Joint Position ----------------------
class JointPositionValue(AsyncWebsocketConsumer):
    group_name = "joint_position_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to arm endpose value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

   
    async def joint_position_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Refresh Arm Data ----------------------
class RefreshArmDataValue(AsyncWebsocketConsumer):
    group_name = "refresh_arm_data_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to arm endpose value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def refresh_arm_data_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Refresh joint Data ----------------------
class RefreshJointDataValue(AsyncWebsocketConsumer):
    group_name = "refresh_joint_data_value_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to arm endpose value"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

   
    async def refresh_joint_data_value_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Joint Heat Return ----------------------
class JointHeatConsumer(AsyncWebsocketConsumer):
    group_name = "joint_heat_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to help"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def joint_heat_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))

# ---------------------- Slot position Return ----------------------
class SlotPatientReturn(AsyncWebsocketConsumer):
    group_name = "slot_group"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "you are connected to help"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def slot_message(self, event):
        payload = event.get("payload")
        await self.send(text_data=json.dumps({"payload": payload}))