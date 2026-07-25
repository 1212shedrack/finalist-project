from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if (instance.is_staff or instance.is_superuser) else 'farmer'
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': role}
        )
    else:
        # Update role if staff status changed
        if hasattr(instance, 'profile'):
            if instance.is_staff or instance.is_superuser:
                UserProfile.objects.filter(user=instance).update(role='admin')
