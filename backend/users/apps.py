from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "User Management"

    def ready(self):
        """
        Import signal handlers when Django starts.

        This method is called exactly once when the application registry
        is fully populated. This is the right place to register signal handlers.
        """
        try:
            import users.signals  # noqa: F401

            print("✅ Users app signals registered")
        except ImportError as e:
            print(f"❌ Failed to import users.signals: {e}")
