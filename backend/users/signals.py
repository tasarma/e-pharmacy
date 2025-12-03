from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from tenants.context import tenant_context_disabled
import structlog

logger = structlog.get_logger(__name__)

User = get_user_model()


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile automatically when User is created"""
    if not created:
        return
    
    # Skip superusers without tenant
    if instance.is_superuser and not instance.tenant_id:
        return
    
    from users.models import UserProfile
    
    try:
        UserProfile.objects.create(
            user=instance,
            tenant=instance.tenant 
        )
        logger.info("user_profile_created", user_id=str(instance.id))
    except Exception as e:
        logger.error(
            "profile_creation_failed",
            user_id=str(instance.id),
            error=str(e)
        )
        raise
