from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from ..models.patient import PInfo
from ..views import jt_medmontcorneal

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

    @patch('corneal_topography.services.cache_service.CacheService.get_patient')
    def test_cached_patient_lookup(self, mock_cache):
        """Test patient data caching."""
        mock_cache.return_value = self.patient
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
        mock_cache.assert_called_once_with('TEST123', 'ORG1')

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Make requests up to the limit
        for _ in range(99):
            self.client.post(
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

        # This request should be rate limited
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
