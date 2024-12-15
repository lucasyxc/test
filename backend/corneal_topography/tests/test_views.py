from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from ..models.patient import PInfo
from ..views import jt_Medmontcorneal

class CornealTopographyViewTests(TestCase):
    """Test corneal topography view functionality."""

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

    @patch('corneal_topography.tasks.process_examination_data.delay')
    def test_valid_post_request(self, mock_process):
        """Test valid POST request processing."""
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

    def test_invalid_file_type(self):
        """Test invalid file type handling."""
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

    @patch('corneal_topography.services.examination_service.ExaminationService.create_or_update_examination')
    @patch('corneal_topography.services.file_service.FileService.process_file')
    def test_cached_patient_lookup(self, mock_file, mock_exam):
        """Test patient data caching."""
        # Setup test data
        mock_file.return_value = {'success': True, 'file_url': '/media/test.jpg'}
        mock_exam.return_value = None

        # First request should cache the patient
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

        # Get the cache key using the same format as CacheService
        from ..services.cache_service import CacheService
        cache_service = CacheService()
        cache_key = cache_service.get_cache_key(f"patient:ORG1", "TEST123")

        # Verify cache was used
        cached_patient = cache.get(cache_key)
        self.assertIsNotNone(cached_patient)
        self.assertEqual(cached_patient.gkid, 'TEST123')

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        with self.settings(RATE_LIMIT={'default': {'LIMIT': 3, 'PERIOD': 60}}):
            # Make requests up to the limit
            for _ in range(3):
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
