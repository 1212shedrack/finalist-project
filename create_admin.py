import os
import django

def create_admin():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amaranthus_project.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    from accounts.models import UserProfile
    
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@amaranthusai.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin@2026!')
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_staff': True, 'is_superuser': True}
    )
    
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = 'admin'
    profile.is_active = True
    profile.save()
    
    if created:
        print(f"[SUCCESS] Created superuser '{username}' automatically.")
    else:
        print(f"[SUCCESS] Reset password & verified superuser '{username}' permissions.")

if __name__ == '__main__':
    create_admin()
