from rest_framework import serializers
from .models import VideoManagementModel

class VideoManagementModelSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = VideoManagementModel
        fields = '__all__'

    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video_image_file and request:
            return request.build_absolute_uri(obj.video_image_file.url)
        return None
    # def get_video_url(self, obj):
    #     if obj.video_image_file:
    #         # force a consistent host, e.g., your server IP or domain
    #         return f"http://192.168.1.33:8000{obj.video_image_file.url}"
    #     return None

# from rest_framework import serializers
# from .models import VideoManagementModel

# class VideoManagementModelSerializer(serializers.ModelSerializer):
#     video_url = serializers.SerializerMethodField()

#     class Meta:
#         model = VideoManagementModel
#         fields = '__all__'

#     def get_video_url(self, obj):
#         request = self.context.get('request')
#         if obj.video_file and request:
#             return request.build_absolute_uri(obj.video_file.url)
#         return obj.video_url