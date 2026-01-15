from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "User Management"

    def ready(self):
        """Import signal handlers when Django starts."""
        try:
            import users.signals  # noqa: F401

            logger.info("User signals successfully registered")
        except Exception as e:
            logger.error(f"Failed to register user signals: {str(e)}", exc_info=True)
            raise
