from django.contrib import admin
from .models import BedDataModel, RoomDataModel, SlotDataModel, RoomPositionModel
# Register your models here.

admin.site.register(BedDataModel)
admin.site.register(RoomDataModel)
admin.site.register(SlotDataModel)
admin.site.register(RoomPositionModel)