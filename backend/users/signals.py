from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile automatically when User is created"""
    if created:
        UserProfile.objects.create(user=instance, tenant=instance.tenant)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile is saved when user is saved"""
    if hasattr(instance, "profile"):
        instance.profile.save()


@receiver(pre_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    """
    Clean up profile when user is deleted (if needed).
    """
    if hasattr(instance, "profile"):
        instance.profile.delete()
