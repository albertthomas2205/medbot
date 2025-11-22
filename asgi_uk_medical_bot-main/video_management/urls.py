from django.urls import path
from .views import update_video, view_all_video, delete_video, swap_video_order, view_active_video
from django.conf import settings

urlpatterns = [

    path('add-video/', update_video, name='add video and update them'),
    path('view-all-video/', view_all_video, name='view every video'),
    path('delete-video/', delete_video, name='delete video'),
    path('swap-video/', swap_video_order, name='swap video order'),
    path('view-active-video/', view_active_video, name='view active video order'),

]