# your_app/migrations/0002_seed_privileges.py

from django.db import migrations

def seed_privileges(apps, schema_editor):
    PrivilegeModel = apps.get_model('privilagecontroller', 'PrivilegeModel')

    privileges = [
        {"code": "admin", "allow_admin": True, "allow_nurse": True},
        {"code": "nurse", "allow_admin": True, "allow_nurse": True},
        {"code": "bp2_checkme_crud", "allow_admin": True, "allow_nurse": True},
        {"code": "video_management_crud", "allow_admin": True, "allow_nurse": True},
        {"code": "room_data_handling_crud", "allow_admin": True, "allow_nurse": True},
        {"code": "patient_data_handling_crud", "allow_admin": True, "allow_nurse": True},
        {"code": "slot_assigning", "allow_admin": True, "allow_nurse": True},
        {"code": "manage_privileges_crud", "allow_admin": True, "allow_nurse": True},
        {"code": "batch_schedule_crud", "allow_admin": True, "allow_nurse": True},
        {"code": "slot_management_crud", "allow_admin": True, "allow_nurse": True},
    ]

    for data in privileges:
        PrivilegeModel.objects.update_or_create(
            code=data["code"], defaults=data
        )

def unseed_privileges(apps, schema_editor):
    PrivilegeModel = apps.get_model('privilagecontroller', 'PrivilegeModel')
    PrivilegeModel.objects.filter(code__in=[
        "admin", "nurse",
        "bp2_checkme_crud", "video_management_crud", "room_data_handling_crud",
        "patient_data_handling_crud", "slot_assigning", "manage_privileges_crud",
        "batch_schedule_crud", "slot_management_crud"
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('privilagecontroller', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_privileges, reverse_code=unseed_privileges),
    ]
