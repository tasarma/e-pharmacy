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
    if not created or instance.is_superuser:
        return

    if not instance.tenant_id:
        logger.warning(
            "user_created_without_tenant",
            user_id=str(instance.id),
            email=instance.email
        )
        return

    from users.models import UserProfile

    try:
        # Superusers might not have tenant context
        with tenant_context_disabled():
            UserProfile.objects.create(user=instance, tenant=instance.tenant)
    except Exception as e:
        logger.error(
            "profile_creation_failed",
            user_id=str(instance.id),
            error=str(e)
        )
        raise
