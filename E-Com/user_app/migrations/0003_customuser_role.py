# Generated manually for role-based authentication.

from django.db import migrations, models


def populate_roles(apps, schema_editor):
    CustomUser = apps.get_model('user_app', 'CustomUser')
    CustomUser.objects.filter(is_superuser=True).update(role='admin')
    CustomUser.objects.filter(is_superuser=False, is_staff=True).update(role='admin')
    CustomUser.objects.filter(is_superuser=False, is_staff=False).update(role='customer')


def sync_staff_flags(apps, schema_editor):
    CustomUser = apps.get_model('user_app', 'CustomUser')
    CustomUser.objects.filter(role='admin').update(is_staff=True)
    CustomUser.objects.exclude(role='admin').update(is_staff=False)


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0002_alter_customuser_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Admin'),
                    ('staff', 'Staff'),
                    ('customer', 'Customer'),
                ],
                default='customer',
                max_length=20,
            ),
        ),
        migrations.RunPython(populate_roles, migrations.RunPython.noop),
        migrations.RunPython(sync_staff_flags, migrations.RunPython.noop),
    ]
