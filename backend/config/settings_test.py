# ruff: noqa: F403, F405
from .settings import *

INSTALLED_APPS += [
    "tests",
]


# Disable migrations just for the "tests" app
class DisableMigrations(dict):
    def __contains__(self, item):
        return True if item == "tests" else False

    def __getitem__(self, item):
        if item == "tests":
            return None
        raise KeyError(item)


MIGRATION_MODULES = DisableMigrations()

# Optional: speed up password hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Optional: use in-memory SQLite for fast tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = "tests.urls"
ALLOWED_HOSTS = ["tenant1.example.com", "tenant2.example.com"]
