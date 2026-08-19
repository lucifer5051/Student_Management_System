from django.db import migrations

def create_default_admin(apps, schema_editor):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

class Migration(migrations.Migration):

    dependencies = [
        ('smsapp', '0003_student_password_student_profile_image'),
    ]

    operations = [
        migrations.RunPython(create_default_admin),
    ]
