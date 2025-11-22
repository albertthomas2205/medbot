from django.urls import path
from .views import upsert_bp2_checkme, list_all_bp2_checkme, toggle_bp2checkme_active,robot_upsert_bp2_checkme

urlpatterns = [

    path('bp2checkme/upsert/', upsert_bp2_checkme, name='upsert_bp2checkme'),
    path('bp2checkme/all/', list_all_bp2_checkme, name='list_all_bp2checkme'),
    path('bp2checkme/toggle-active/', toggle_bp2checkme_active, name='toggle_bp2checkme_active'),

    path('robot/bp2checkme/upsert/', robot_upsert_bp2_checkme, name='from robot upsert_bp2checkme'),

]