import os
from typing import Dict, Any, Tuple
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from ..utils.validators import validate_file_type, validate_file_size

class FileService:
    """Service for handling file operations."""

    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self, storage: FileSystemStorage = None):
        self.storage = storage or FileSystemStorage()

    def process_file(self, file: UploadedFile) -> Dict[str, Any]:
        """
        Process uploaded file with validation and storage.

        Args:
            file: Uploaded file object

        Returns:
            Dict containing success status and file information or error message
        """
        try:
            filename, file_url = self.save_file(file)
            return {
                'success': True,
                'file_url': file_url,
                'filename': filename
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def save_file(self, file: UploadedFile) -> Tuple[str, str]:
        """
        Save uploaded file after validation.

        Returns:
            Tuple[str, str]: Tuple of (filename, file_url)
        """
        validate_file_type(file, self.ALLOWED_EXTENSIONS)
        validate_file_size(file, self.MAX_FILE_SIZE)

        filename = self.storage.save(file.name, file)
        file_url = self.storage.url(filename)

        return filename, file_url

    def delete_file(self, filename: str) -> None:
        """Delete file if it exists."""
        if self.storage.exists(filename):
            self.storage.delete(filename)
