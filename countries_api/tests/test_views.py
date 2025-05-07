from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from rest_framework.request import Request
from types import SimpleNamespace
from django.http import HttpResponse
from django.db.models import Q

from unittest.mock import patch, MagicMock
from rest_framework.test import APITestCase, force_authenticate

from countries_api.models import Country
from countries_api.views import (
    CountryViewSet, 
    country_list_view, 
    country_detail_view, 
    register_view, 
    login_view
)


class TestViewSetup(TestCase):
    """Base test class with common setup for views tests"""
    
    def setUp(self):
        # Create a test user
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(
            username=self.username, 
            password=self.password
        )
        
        # Set up client and request factory
        self.client = Client()
        self.factory = RequestFactory()
        
        # Create mock Country objects
        self.country_data = {
            'name': 'Test Country',
            'official_name': 'The Republic of Test',
            'cca2': 'TC',
            'cca3': 'TCY',
            'region': 'Test Region',
            'subregion': 'Test Subregion',
            'population': 1000000,
            'flag': 'https://example.com/flag.png',
            'timezones': ['UTC+01:00'],
            'capitals': ['Testville'],
            'languages': {'test': 'Testish'},
            'currencies': {'TST': {'name': 'Test Dollar', 'symbol': 'T$'}}
        }
        
    def _add_session_to_request(self, request):
        """Helper method to add session to request"""
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()
        
        # Add messages middleware
        middleware = MessageMiddleware(lambda r: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)
        
        # Add auth middleware
        middleware = AuthenticationMiddleware(lambda r: None)
        middleware.process_request(request)
        
        return request


class CountryViewSetTest(APITestCase):
    """Tests for the CountryViewSet class"""
    
    def setUp(self):
        # Create a test user
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(
            username=self.username, 
            password=self.password
        )
        
        # Set up request factory
        self.factory = RequestFactory()
        
        # Set up the viewset
        self.viewset = CountryViewSet()
    
    @patch('countries_api.views.render')
    @patch('countries_api.views.Country.objects.all')
    @patch('countries_api.views.Country.objects.filter')
    def test_same_region(self, mock_filter, mock_all, mock_render):
        """Test the same_region action"""
        # Setup mock country
        mock_country = MagicMock()
        mock_country.region = 'Test Region'
        mock_country.id = 1

        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset
        mock_queryset.exclude.return_value = [MagicMock()]

        # Mock render to avoid loading template
        mock_render.return_value = HttpResponse('Mocked HTML')

        # Create request
        request = self.factory.get('/api/countries/1/same_region/')
        force_authenticate(request, user=self.user)

        # Mock get_object
        self.viewset.get_object = MagicMock(return_value=mock_country)

        # Call the action
        response = self.viewset.same_region(request, pk=1)

        # Assertions
        mock_filter.assert_called_once_with(region='Test Region')
        mock_queryset.exclude.assert_called_once_with(id=1)
        mock_render.assert_called_once()  # confirm render was called
        self.assertEqual(response.status_code, 200)
    
    @patch('countries_api.views.render')
    @patch('countries_api.views.Country.objects.all')
    def test_by_language(self, mock_all, mock_render):
        """Test the by_language action"""
        # Setup mock countries
        mock_country1 = MagicMock()
        mock_country1.languages = {'en': 'English', 'fr': 'French'}
        mock_country2 = MagicMock()
        mock_country2.languages = {'es': 'Spanish'}

        mock_all.return_value = [mock_country1, mock_country2]

        # Mock render to avoid loading template
        mock_render.return_value = HttpResponse('Mocked HTML')

        # Create request and wrap in DRF Request
        django_request = self.factory.get('/api/countries/by_language/', {'language': 'english'})
        request = Request(django_request)
        force_authenticate(django_request, user=self.user)

        # Setup viewset
        self.viewset.request = request

        # Call the action
        response = self.viewset.by_language(request)

        # Assertions
        mock_all.assert_called_once()
        mock_render.assert_called_once()  # confirm render was called
        self.assertEqual(response.status_code, 200)
        
    @patch('countries_api.views.render')
    @patch('countries_api.views.Country.objects.filter')
    def test_search_with_query(self, mock_filter, mock_render):
        """Test the search action with query parameter"""
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset

        # Mock render to avoid loading actual template
        mock_render.return_value = HttpResponse('Mocked HTML')

        # Create request
        request = self.factory.get('/api/countries/search/', {'q': 'test'})
        force_authenticate(request, user=self.user)

        # Wrap in DRF Request
        drf_request = Request(request)

        # Setup viewset
        self.viewset.request = drf_request

        # Call the action
        response = self.viewset.search(drf_request)

        # Assertions
        self.assertEqual(response.status_code, 200)

        expected_query = Q(name__icontains='test') | Q(official_name__icontains='test')
        mock_filter.assert_called_once_with(expected_query)

        mock_render.assert_called_once()
    
    @patch('countries_api.views.render')
    def test_search_without_query(self, mock_render):
        """Test the search action without query parameter"""

        # Setup mock return (simulate a response object)
        mock_render.return_value.status_code = 200

        # Create Django request
        django_request = self.factory.get('/api/countries/search/')
        force_authenticate(django_request, user=self.user)

        # Wrap it in DRF Request
        request = Request(django_request)

        # Assign to viewset
        self.viewset.request = request

        # Call the action
        response = self.viewset.search(request)

        # Assertions
        self.assertEqual(response.status_code, 200)

        # Optionally: assert render called
        mock_render.assert_called_once()

    def test_get_serializer_class(self):
        """Test the get_serializer_class method"""
        # Test list action
        self.viewset.action = 'list'
        self.assertEqual(self.viewset.get_serializer_class().__name__, 'CountryListSerializer')
        
        # Test create action
        self.viewset.action = 'create'
        self.assertEqual(self.viewset.get_serializer_class().__name__, 'CountryCreateUpdateSerializer')
        
        # Test update action
        self.viewset.action = 'update'
        self.assertEqual(self.viewset.get_serializer_class().__name__, 'CountryCreateUpdateSerializer')
        
        # Test retrieve action (default)
        self.viewset.action = 'retrieve'
        self.assertEqual(self.viewset.get_serializer_class().__name__, 'CountrySerializer')


class CountryViewsTest(TestViewSetup):
    """Tests for the country_list_view and country_detail_view functions"""
    
    @patch('countries_api.views.Country.objects.all')
    @patch('countries_api.views.Country.objects.filter')
    def test_country_list_view_no_search(self, mock_filter, mock_all):
        """Test country_list_view without search query"""
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_all.return_value = mock_queryset
        
        # Create request
        request = self.factory.get('/countries/')
        request.user = self.user
        
        # Call the view
        response = country_list_view(request)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_all.assert_called_once()
        mock_filter.assert_not_called()
    
    @patch('countries_api.views.Country.objects.filter')
    def test_country_list_view_with_search(self, mock_filter):
        """Test country_list_view with search query"""
        # Setup mock queryset
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset
        
        # Create request
        request = self.factory.get('/countries/', {'q': 'test'})
        request.user = self.user
        
        # Call the view
        response = country_list_view(request)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_filter.assert_called_once()
    
    @patch('countries_api.views.get_object_or_404')
    @patch('countries_api.views.Country.objects.filter')
    def test_country_detail_view(self, mock_filter, mock_get_object):
        """Test country_detail_view"""
        # Setup mock country (using SimpleNamespace for better template compatibility)
        mock_country = SimpleNamespace(id=1, region='Test Region')
        mock_get_object.return_value = mock_country

        # Setup mock queryset
        mock_same_region_country = SimpleNamespace(id=2, name='Other Country')
        mock_queryset = MagicMock()
        mock_queryset.exclude.return_value = [mock_same_region_country]
        mock_filter.return_value = mock_queryset

        # Create request
        request = self.factory.get('/countries/1/')
        request.user = self.user

        # Call the view
        response = country_detail_view(request, country_id=1)

        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_get_object.assert_called_once_with(Country, id=1)
        mock_filter.assert_called_once_with(region='Test Region')
        mock_queryset.exclude.assert_called_once_with(id=1)


class AuthViewsTest(TestViewSetup):
    """Tests for the authentication views"""
    
    def test_register_view_get(self):
        """Test register_view GET request"""
        # Create request
        request = self.factory.get('/accounts/register/')
        response = register_view(request)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
    
    
    @patch('countries_api.views.authenticate')
    @patch('countries_api.views.UserCreationForm')
    def test_register_view_post_valid(self, mock_form, mock_authenticate):
        """Test register_view POST with valid data"""
        # Setup mock form and user
        form_instance = MagicMock()
        form_instance.is_valid.return_value = True
        form_instance.cleaned_data = {
            'username': 'newuser',
            'password1': 'testpass123'
        }
        mock_form.return_value = form_instance
        
        # Setup mock authenticate
        mock_user = MagicMock()
        mock_user.backend = 'django.contrib.auth.backends.ModelBackend'  # ✅ Add this line
        mock_authenticate.return_value = mock_user
        
        # Create request
        request = self.factory.post('/accounts/register/', {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        request = self._add_session_to_request(request)
        
        # Call the view
        response = register_view(request)
        
        # Assertions
        self.assertEqual(response.status_code, 302)  # Redirect
        form_instance.save.assert_called_once()
        mock_authenticate.assert_called_once()

    @patch('countries_api.views.UserCreationForm')
    def test_register_view_post_invalid(self, mock_form):
        """Test register_view POST with invalid data"""
        # Setup mock form
        form_instance = MagicMock()
        form_instance.is_valid.return_value = False
        mock_form.return_value = form_instance
        
        # Create request
        request = self.factory.post('/accounts/register/', {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'different'  # Password mismatch
        })
        
        # Call the view
        response = register_view(request)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        form_instance.save.assert_not_called()
    
    def test_login_view_get(self):
        """Test login_view GET request"""
        # Create request
        request = self.factory.get('/accounts/login/')
        response = login_view(request)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
    
    @patch('countries_api.views.authenticate')
    def test_login_view_post_valid(self, mock_authenticate):
        """Test login_view POST with valid credentials"""
        # Setup mock authenticate
        mock_user = MagicMock()
        mock_user.username = 'testuser'
        mock_user.backend = 'django.contrib.auth.backends.ModelBackend'  # ✅ add backend
        mock_authenticate.return_value = mock_user
        
        # Create request
        request = self.factory.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        request = self._add_session_to_request(request)
        
        # Call the view
        response = login_view(request)
        
        # Assertions
        self.assertEqual(response.status_code, 302)  # Redirect
        mock_authenticate.assert_called_once()
    
    @patch('countries_api.views.authenticate')
    def test_login_view_post_invalid(self, mock_authenticate):
        """Test login_view POST with invalid credentials"""
        # Setup mock authenticate to return None (authentication failed)
        mock_authenticate.return_value = None
        
        # Create request
        request = self.factory.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        request = self._add_session_to_request(request)
        
        # Call the view
        response = login_view(request)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_authenticate.assert_called_once()


class IntegrationTests(TestCase):
    """Integration tests for views with Client"""
    
    def setUp(self):
        # Create a test user
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(
            username=self.username, 
            password=self.password
        )
        
        # Setup client
        self.client = Client()
        
        # Create a test country
        self.country_data = {
            'name': 'Test Country',
            'official_name': 'The Republic of Test',
            'cca2': 'TC',
            'cca3': 'TCY',
            'region': 'Test Region',
            'subregion': 'Test Subregion',
            'population': 1000000,
            'flag': 'https://example.com/flag.png',
            'timezones': ['UTC+01:00'],
            'capitals': ['Testville'],
            'languages': {'test': 'Testish'},
            'currencies': {'TST': {'name': 'Test Dollar', 'symbol': 'T$'}}
        }
    
    @patch('countries_api.views.Country.objects.all')
    @patch('countries_api.views.Country.objects.filter')
    def test_country_list_view_integration(self, mock_filter, mock_all):
        """Integration test for country_list_view"""
        # Setup mock queryset
        mock_queryset = MagicMock()
        # Make the mock behave like a queryset
        mock_queryset.__iter__.return_value = []
        mock_all.return_value = mock_queryset
        mock_filter.return_value = mock_queryset
        
        # Login
        self.client.login(username=self.username, password=self.password)
        
        # Test with no search query
        response = self.client.get(reverse('country_list'))
        self.assertEqual(response.status_code, 200)
        mock_all.assert_called()
        
        # Test with search query
        response = self.client.get(reverse('country_list') + '?q=test')
        self.assertEqual(response.status_code, 200)
        mock_filter.assert_called()
    
    @patch('countries_api.views.get_object_or_404')
    @patch('countries_api.views.Country.objects.filter')
    def test_country_detail_view_integration(self, mock_filter, mock_get_object):
        """Integration test for country_detail_view"""
        # Setup mock country and queryset
        mock_country = MagicMock()
        mock_country.id = 1
        mock_country.region = 'Test Region'
        mock_get_object.return_value = mock_country
        
        mock_queryset = MagicMock()
        # Make the mock behave like a queryset
        mock_queryset.__iter__.return_value = []
        mock_queryset.exclude.return_value = []
        mock_filter.return_value = mock_queryset
        
        # Login
        self.client.login(username=self.username, password=self.password)
        
        # Test detail view
        response = self.client.get(reverse('country_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        mock_get_object.assert_called_once()
        mock_filter.assert_called_once_with(region='Test Region')
        mock_queryset.exclude.assert_called_once_with(id=1)
    
    def test_login_view_integration(self):
        """Integration test for login_view"""
        # Test GET request
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request with valid credentials
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Test POST request with invalid credentials
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_register_view_integration(self):
        """Integration test for register_view"""
        # Test GET request
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request with valid data
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'Complex_pass123',
            'password2': 'Complex_pass123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Test POST request with invalid data
        response = self.client.post(reverse('register'), {
            'username': 'anotheruser',
            'password1': 'Complex_pass123',
            'password2': 'Different_pass123'  # Password mismatch
        })
        self.assertEqual(response.status_code, 200)