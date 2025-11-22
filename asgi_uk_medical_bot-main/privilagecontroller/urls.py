from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('create-privilege/', create_or_update_privilege, name='create-privilege'),
    path('view-all-privilege/', view_all_privileges, name='view every privilege data'),

]