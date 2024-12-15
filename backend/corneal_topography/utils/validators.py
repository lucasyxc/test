import os
from typing import Set
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError

def validate_file_type(file: UploadedFile, allowed_extensions: Set[str]) -> None:
    """Validate file type based on extension."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")

def validate_file_size(file: UploadedFile, max_size: int) -> None:
    """Validate file size."""
    if file.size > max_size:
        raise ValidationError(f"File size exceeds maximum allowed size of {max_size/1024/1024}MB")

def validate_measurement_values(value: float, min_value: float, max_value: float, field_name: str) -> None:
    """Validate measurement values are within acceptable range."""
    if value is not None and (value < min_value or value > max_value):
        raise ValidationError(f"{field_name} must be between {min_value} and {max_value}")
