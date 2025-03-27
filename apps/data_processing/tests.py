from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from apps.data_processing.models import CaseMetadata, FactPattern, SentencingRange, Offence
from datetime import datetime

class DataProcessingTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test data
        self.case = CaseMetadata.objects.create(
            case_id='2023ABPC123',
            style_of_cause='R v Smith',
            citation='2023 ABPC 123',
            year=2023,
            court='ABPC',
            decision_number=123,
            jurisdiction='Alberta',
            court_name='Alberta Provincial Court',
            court_level='Provincial Court',
            short_url='https://example.com/2023abpc123',
            language='en',
            docket_number=12345,
            decision_date=timezone.now()
        )
        
        self.offence = Offence.objects.create(
            section='cc266',
            offence_name='Assault',
            minimum_summary='None',
            maximum_summary='6 months imprisonment',
            minimum_indictable='None',
            maximum_indictable='5 years imprisonment'
        )

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_case_metadata_api(self):
        """Test the CaseMetadata API endpoints"""
        url = reverse('casemetadata-list')
        
        # Test GET list
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test POST
        new_case_data = {
            'case_id': '2023ABPC124',
            'style_of_cause': 'R v Jones',
            'citation': '2023 ABPC 124',
            'year': 2023,
            'court': 'ABPC',
            'decision_number': 124,
            'jurisdiction': 'Alberta',
            'court_name': 'Alberta Provincial Court',
            'court_level': 'Provincial Court',
            'short_url': 'https://example.com/2023abpc124',
            'language': 'en',
            'docket_number': 12346,
            'decision_date': timezone.now().isoformat()
        }
        response = self.client.post(url, new_case_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_offence_api(self):
        """Test the Offence API endpoints"""
        url = reverse('offence-list')
        
        # Test GET list
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtering
        response = self.client.get(f"{url}?section=cc266")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['section'], 'cc266')

    def test_authentication_required(self):
        """Test that authentication is required for API access"""
        # Create an unauthenticated client
        client = APIClient()
        
        # Try to access the API without authentication
        url = reverse('casemetadata-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_home_page(self):
        """Test that the home page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'core/home.html')
