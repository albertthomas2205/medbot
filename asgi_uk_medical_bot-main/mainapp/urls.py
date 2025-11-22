from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('login/', login_view, name='login-admin'),
    # Create admin and nurse in this urls
    path('create-admin/', create_or_update_admin_data, name='create-admin'),
    path('view-all-admin/<str:role>/', view_all_admin_users, name='view every admin data'),
    path('delete-admin/<int:user_id>/', soft_delete_admin_user, name='view every admin data'),
    # Create patient in this urls
    path('create-patient/', create_or_update_patient_data, name='create-patient'),
    path('view-all-patient/', view_all_patient, name='view every patient data'),
    path('delete-patient/<int:patient_id>/', soft_delete_patient, name='view every patient data'),
    path('delete-all-patient/', delete_all_patient, name='delete all patient data'),
    # Edit room and bet assigned for patient
    # path('reassign-bed-room/', reassign_designation, name='change bed or room designation'),
    # Assign room to patient
    path('assign-bed-room/', assign_designation, name='assign bed or room designation'),

    path('create-update-local-ip/', create_update_local_ip, name='create or update local ip'),
    path('get-local-ip/', get_local_ip, name='get local ip'),
    path('drop_bp2checkme_table/', drop_bp2checkme_table, name='get drop_bp2checkme_table'),

    path('export_patients_excel/', export_patients_excel, name='export patients excel'),
    path('import_patients_excel/', import_patients_excel, name='import patients excel'),

]