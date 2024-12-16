from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from ..models.patient import PInfo
from ..views import jt_Medmontcorneal, get_ocr_service
import pytest
import logging

class CornealTopographyViewTests(TestCase):
    """Test corneal topography view functionality."""

    @patch('corneal_topography.views._ocr_service', None)
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        self.patient = PInfo.objects.create(
            gkid="TEST123",
            organizationid="ORG1",
            name="Test Patient"
        )
        self.valid_file = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        # Clear cache before each test
        cache.clear()

    def tearDown(self):
        """Clean up after each test."""
        cache.clear()
        # Clean up media files
        import shutil, os
        if os.path.exists('media'):
            shutil.rmtree('media')

    @patch('corneal_topography.views.get_ocr_service')
    @patch('corneal_topography.tasks.process_examination_data.delay')
    def test_valid_post_request(self, mock_process, mock_get_ocr):
        """Test valid POST request processing."""
        # Setup mock OCR
        mock_ocr_service = Mock()
        mock_ocr_service.process_image.return_value = {
            'text_blocks': [{'text': 'K1: 43.5', 'confidence': 0.99}],
            'rotation_angle': 0
        }
        mock_get_ocr.return_value = mock_ocr_service

        response = self.client.post(
            reverse('corneal_topography'),
            data={
                'file': self.valid_file,
                'organization_id': 'ORG1',
                'gkid': 'TEST123',
                'type': 'standard',
                'eye': 'right'
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, 200)
        mock_process.assert_called_once()

    @patch('corneal_topography.views.get_ocr_service')
    def test_invalid_file_type(self, mock_get_ocr):
        """Test invalid file type handling."""
        # Setup mock OCR
        mock_ocr_service = Mock()
        mock_get_ocr.return_value = mock_ocr_service

        response = self.client.post(
            reverse('corneal_topography'),
            data={
                'file': SimpleUploadedFile(
                    "test.txt",
                    b"file_content",
                    content_type="text/plain"
                ),
                'organization_id': 'ORG1',
                'gkid': 'TEST123',
                'type': 'standard',
                'eye': 'right'
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, 400)
        mock_ocr_service.process_image.assert_not_called()

    @patch('corneal_topography.views.get_ocr_service')
    @patch('corneal_topography.tasks.process_examination_data.delay')
    @patch('corneal_topography.services.examination_service.ExaminationService.create_or_update_examination')
    @patch('corneal_topography.services.file_service.FileService.validate_and_save_file')
    @patch('corneal_topography.services.cache_service.CacheService.get_patient')
    @patch('corneal_topography.services.cache_service.CacheService.set_patient')
    def test_cached_patient_lookup(
        self, mock_set_patient, mock_get_patient, mock_file,
        mock_exam, mock_task, mock_get_ocr
    ):
        """Test patient data caching."""
        # Setup mock OCR
        mock_ocr_service = Mock()
        mock_ocr_service.process_image.return_value = {
            'text_blocks': [{'text': 'K1: 43.5', 'confidence': 0.99}],
            'rotation_angle': 0
        }
        mock_get_ocr.return_value = mock_ocr_service

        # Setup test data
        mock_file.return_value = (True, None, '/media/test.jpg')  # success, error_msg, file_url
        mock_exam.return_value = None
        mock_get_patient.return_value = None  # First call returns None (cache miss)
        mock_task.return_value = None

        # First request should trigger cache set
        response = self.client.post(
            reverse('corneal_topography'),
            data={
                'file': self.valid_file,
                'organization_id': 'ORG1',
                'gkid': 'TEST123',
                'type': 'standard',
                'eye': 'right'
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, 200)

        # Verify cache operations
        mock_get_patient.assert_called_once()
        mock_set_patient.assert_called_once()
        mock_task.assert_called_once()

        # Second request should use cached data
        mock_get_patient.reset_mock()
        mock_get_patient.return_value = self.patient  # Second call returns cached patient
        mock_task.reset_mock()

        response = self.client.post(
            reverse('corneal_topography'),
            data={
                'file': self.valid_file,
                'organization_id': 'ORG1',
                'gkid': 'TEST123',
                'type': 'standard',
                'eye': 'right'
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, 200)
        mock_get_patient.assert_called_once()  # Verify cache was checked
        mock_set_patient.assert_called_once()  # Should still be called only once from first request
        mock_task.assert_called_once()  # Task should still be called for new examination

    @pytest.mark.timeout(10)  # Set 10-second timeout
    @patch('corneal_topography.views.get_ocr_service')
    @patch('corneal_topography.tasks.process_examination_data.delay')
    def test_rate_limiting(self, mock_task, mock_get_ocr):
        """Test rate limiting functionality."""
        # Setup mock OCR
        mock_ocr_service = Mock()
        mock_ocr_service.process_image.return_value = {
            'text_blocks': [{'text': 'K1: 43.5', 'confidence': 0.99}],
            'rotation_angle': 0
        }
        mock_get_ocr.return_value = mock_ocr_service

        import time
        logger = logging.getLogger('corneal_topography.services.rate_limiter')
        logger.setLevel(logging.DEBUG)
        mock_task.return_value = None

        with self.settings(RATE_LIMIT={
            'corneal_topography': {  # Use correct key matching the decorator
                'LIMIT': 3,
                'PERIOD': 60
            }
        }):
            # Make requests up to the limit
            for i in range(3):
                logger.debug(f"Making request {i+1} of 3")
                response = self.client.post(
                    reverse('corneal_topography'),
                    data={
                        'file': self.valid_file,
                        'organization_id': 'ORG1',
                        'gkid': 'TEST123',
                        'type': 'standard',
                        'eye': 'right'
                    },
                    format='multipart'
                )
                self.assertEqual(response.status_code, 200)
                time.sleep(0.1)  # Small delay between requests

            logger.debug("Making rate-limited request")
            # Next request should be rate limited
            response = self.client.post(
                reverse('corneal_topography'),
                data={
                    'file': self.valid_file,
                    'organization_id': 'ORG1',
                    'gkid': 'TEST123',
                    'type': 'standard',
                    'eye': 'right'
                },
                format='multipart'
            )
            self.assertEqual(response.status_code, 429)
            self.assertIn('Rate limit exceeded', str(response.content))
