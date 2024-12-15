import unittest
from unittest.mock import Mock, patch
from datetime import date
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from ..models.examination import PatientExaminationRecords
from ..models.patient import PInfo
from ..services.file_service import FileService
from ..services.examination_service import ExaminationService
from ..services.cache_service import CacheService
from ..utils.validators import validate_file_type, validate_file_size

class FileServiceTests(TestCase):
    """Test file handling service."""

    def setUp(self):
        self.service = FileService()
        self.valid_file = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.invalid_file = SimpleUploadedFile(
            "test.txt",
            b"file_content",
            content_type="text/plain"
        )

    def test_valid_file_upload(self):
        """Test uploading a valid file."""
        filename, url = self.service.save_file(self.valid_file)
        self.assertTrue(filename.endswith('.jpg'))
        self.assertTrue(url.startswith('/media/'))

    def test_invalid_file_type(self):
        """Test uploading an invalid file type."""
        with self.assertRaises(ValidationError):
            self.service.save_file(self.invalid_file)

    def test_file_size_limit(self):
        """Test file size validation."""
        large_file = SimpleUploadedFile(
            "large.jpg",
            b"x" * (FileService.MAX_FILE_SIZE + 1),
            content_type="image/jpeg"
        )
        with self.assertRaises(ValidationError):
            self.service.save_file(large_file)

class ExaminationServiceTests(TestCase):
    """Test examination service."""

    def setUp(self):
        self.service = ExaminationService()
        self.patient = PInfo.objects.create(
            gkid="TEST123",
            organizationid="ORG1",
            name="Test Patient"
        )

    @patch('django.db.transaction.atomic')
    def test_create_examination(self, mock_atomic):
        """Test creating a new examination record."""
        exam_data = {
            'patient_id': self.patient.id,
            'organization_id': 'ORG1',
            'examination_date': date.today(),
            'corneal_topography_right_eye_k1': 23.5,
            'corneal_topography_right_eye_k2': 24.0,
            'corneal_topography_right_eye_k1_axis': 90,
            'corneal_topography_right_eye_k2_axis': 180,
        }
        record = self.service.create_or_update_examination(**exam_data)
        self.assertIsInstance(record, PatientExaminationRecords)
        self.assertEqual(record.corneal_topography_right_eye_k1, 23.5)
        self.assertEqual(record.corneal_topography_right_eye_k2, 24.0)
        self.assertEqual(record.corneal_topography_right_eye_k1_axis, 90)
        self.assertEqual(record.corneal_topography_right_eye_k2_axis, 180)

    def test_update_existing_examination(self):
        """Test updating an existing examination record."""
        # Create initial record
        initial_data = {
            'patient_id': self.patient.id,
            'organization_id': 'ORG1',
            'examination_date': date.today(),
            'corneal_topography_right_eye_k1': 23.5,
        }
        record = self.service.create_or_update_examination(**initial_data)

        # Update record
        update_data = {
            'patient_id': self.patient.id,
            'organization_id': 'ORG1',
            'examination_date': date.today(),
            'corneal_topography_right_eye_k1': 24.0,
        }
        updated_record = self.service.create_or_update_examination(**update_data)
        self.assertEqual(updated_record.corneal_topography_right_eye_k1, 24.0)

    def test_invalid_patient(self):
        """Test handling invalid patient ID."""
        exam_data = {
            'patient_id': 99999,  # Non-existent patient ID
            'organization_id': 'ORG1',
            'examination_date': date.today(),
        }
        with self.assertRaises(ValidationError):
            self.service.create_or_update_examination(**exam_data)

class CacheServiceTests(TestCase):
    """Test caching service."""

    def setUp(self):
        self.service = CacheService()
        self.patient = PInfo.objects.create(
            gkid="TEST123",
            organizationid="ORG1",
            name="Test Patient"
        )

    def test_patient_cache(self):
        """Test patient data caching."""
        # Cache patient data
        self.service.set_patient(
            self.patient.gkid,
            self.patient.organizationid,
            self.patient
        )

        # Retrieve from cache
        cached_patient = self.service.get_patient(
            self.patient.gkid,
            self.patient.organizationid
        )
        self.assertEqual(cached_patient.id, self.patient.id)

    def test_cache_invalidation(self):
        """Test cache invalidation."""
        # Set and then invalidate cache
        self.service.set_patient(
            self.patient.gkid,
            self.patient.organizationid,
            self.patient
        )
        self.service.invalidate_patient(
            self.patient.gkid,
            self.patient.organizationid
        )

        # Should return None after invalidation
        cached_patient = self.service.get_patient(
            self.patient.gkid,
            self.patient.organizationid
        )
        self.assertIsNone(cached_patient)

if __name__ == '__main__':
    unittest.main()
