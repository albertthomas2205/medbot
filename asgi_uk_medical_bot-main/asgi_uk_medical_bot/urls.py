"""
URL configuration for asgi_uk_medical_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse
from django.conf.urls.static import static
from django.urls import path, include, re_path

from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
# from drf_spectacular.views import (
#     SpectacularAPIView,
#     SpectacularSwaggerView,
#     SpectacularRedocView,
# )

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="MEDICAL BOAT API",
        default_version='v1',
        description="API documentation for my project",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


   


def health_check(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
    
    path('admin/', admin.site.urls),
    path('api/medicalbot/main/',include('mainapp.urls')),
    path('api/medicalbot/privilege/',include('privilagecontroller.urls')),
    path('api/medicalbot/bed/data/',include('bed_data.urls')),
    path('api/medicalbot/schedule/',include('schedule_rounds.urls')),
    path('api/medicalbot/video_management/',include('video_management.urls')),
    path('api/medicalbot/vitals_management/',include('vitals_management.urls')),
    path('api/medicalbot/robot_management/',include('robot_management.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)