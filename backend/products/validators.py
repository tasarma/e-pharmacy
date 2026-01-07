from django.core.exceptions import ValidationError

def validate_image_size(file):
    """
    Validates that the file size is under a specific limit (e.g., 5MB).
    """
    limit_mb = 5
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Max size of file is {limit_mb} MB")
