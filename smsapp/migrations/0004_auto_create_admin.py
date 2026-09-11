from django.db import migrations

def create_default_admin(apps, schema_editor):
    from django.contrib.auth.hashers import make_password
    from django.utils import timezone
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user WHERE username = %s", ['admin'])
        row = cursor.fetchone()
        if not row or row[0] == 0:
            hashed_pw = make_password('admin123')
            now = timezone.now()
            cursor.execute(
                """
                INSERT INTO auth_user (
                    password, last_login, is_superuser, username,
                    first_name, last_name, email, is_staff, is_active, date_joined
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [hashed_pw, None, 1, 'admin', '', '', 'admin@example.com', 1, 1, now]
            )

class Migration(migrations.Migration):

    dependencies = [
        ('smsapp', '0003_student_password_student_profile_image'),
    ]

    operations = [
        migrations.RunPython(create_default_admin),
    ]
