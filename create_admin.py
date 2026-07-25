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
    
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(username=username, email=email, password=password)
        # Ensure UserProfile exists with admin role
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = 'admin'
        profile.save()
        print(f"[SUCCESS] Created superuser '{username}' automatically.")
    else:
        print(f"[INFO] Superuser '{username}' already exists.")

if __name__ == '__main__':
    create_admin()
