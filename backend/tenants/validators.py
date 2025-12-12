from django.core.exceptions import ValidationError


def validate_business_email(email: str) -> None:
    """Reject disposable email providers."""
    DISPOSABLE_DOMAINS = {
        "tempmail.com",
        "guerrillamail.com",
        "mailinator.com",
        "10minutemail.com",
        "throwaway.email",
    }

    domain = email.split("@")[-1].lower()
    if domain in DISPOSABLE_DOMAINS:
        raise ValidationError("Disposable email addresses are not allowed")


def validate_tenant_name(name: str) -> None:
    """Prevent suspicious tenant names."""
    BLOCKED_KEYWORDS = {"test", "admin", "root", "system", "null", "demo"}

    if name.lower().strip() in BLOCKED_KEYWORDS:
        raise ValidationError(f"Tenant name '{name}' is not allowed")

    if len(name.strip()) < 3:
        raise ValidationError("Tenant name must be at least 3 characters")
