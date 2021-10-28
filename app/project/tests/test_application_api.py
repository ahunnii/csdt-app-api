from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Application

from project.serializers import ApplicationSerializer, \
                                ApplicationDetailSerializer

APPLICATIONS_URL = reverse('project:application-list')


def detail_url(app_id):
    """Return application detail url"""
    return reverse('project:application-detail', args=[app_id])


def sample_application(name='Test App', **params):
    """Create and return a sample application"""
    defaults = {
        'name': name,
        'link': f'{name}/index.html',
        'description': f'Test Description of {name}'
    }
    defaults.update(params)

    return Application.objects.create(**defaults)


class PublicApplicationsApiTests(TestCase):
    """Test unauthenticated application api access"""

    def setUp(self):
        self.client = APIClient()
        self.app1 = sample_application(name='Adinkra')
        self.app2 = sample_application(name='Henna')
        self.app3 = sample_application(name='Rhythm Wheels')

    def test_retrieve_applications_unauthenticated(self):
        """Test that unauthenticated users view list of applications"""
        res = self.client.get(APPLICATIONS_URL)

        applications = Application.objects.all().order_by('-id')
        serializer = ApplicationSerializer(applications, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_unauthenticated_create_application(self):
        """Test that unauthenticated users cannot create new app"""
        payload = {
            'name': 'Cool App',
            'link': 'something/index.html',
            'description': 'some description',
        }

        res = self.client.post(APPLICATIONS_URL, payload=payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_application_details_unauthenticated(self):
        """Test that unauthenticated users can retrieve details"""
        url = detail_url(self.app1.id)

        res = self.client.get(url)

        serializer = ApplicationDetailSerializer(self.app1)
        self.assertEqual(res.data, serializer.data)

    def test_unable_to_update_app(self):
        """Test that unauthenticated users cannot update application"""
        payload = {"name": "Adinkra Pro"}
        url = detail_url(self.app1.id)
        res = self.client.patch(url, payload)

        self.app1.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(self.app1.name, payload['name'])

        res = self.client.put(url, payload)
        self.app1.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(self.app1.name, payload['name'])


class PrivateApplicationsApiTests(TestCase):
    """Tests for authenticated users for application api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test",
            "test@csdt.org",
            "testpass"
        )
        self.client.force_authenticate(self.user)

        self.app1 = sample_application(name='Cornrow Curves')

    def test_retrieve_applications(self):
        """Test retrieving applications"""
        res = self.client.get(APPLICATIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unable_to_create_application(self):
        """Test non staff members cannot create new app"""
        payload = {
            "name": "New App",
            "link": "newapp/index.html",
            "description": "new"
        }

        res = self.client.post(APPLICATIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unable_to_update_application(self):
        """Test non staff members cannot update app"""
        payload = {"name": "Adinkra Pro"}
        url = detail_url(self.app1.id)
        res = self.client.patch(url, payload)

        self.app1.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(self.app1.name, payload['name'])

        res = self.client.put(url, payload)
        self.app1.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(self.app1.name, payload['name'])


class StaffApplicationsApiTests(TestCase):
    """Tests for staff members using application api"""

    def setUp(self):
        self.client = APIClient()
        self.staff = get_user_model().objects.create_superuser(
            "admin",
            "admin@csdt.org",
            "testpassword"
        )
        self.client.force_authenticate(self.staff)

        self.app1 = sample_application(name='Skateboarding')

    def test_retrieve_applications_staff(self):
        """Test retrieving applications as a staff member"""
        res = self.client.get(APPLICATIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_application(self):
        """Test staff ability to create new app"""
        payload = {
            "name": "Bead Loom",
            "link": "beadloom/index.html",
            "description": "Bead Loom JS"
        }

        res = self.client.post(APPLICATIONS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        application = Application.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(application, key))

    def test_partial_update_application(self):
        """Test staff update to application with patch"""
        payload = {"name": "Adinkra Pro"}
        url = detail_url(self.app1.id)
        self.client.patch(url, payload)

        self.app1.refresh_from_db()
        self.assertEqual(self.app1.name, payload['name'])

    def test_full_update_application(self):
        """Test staff update to application with patch"""
        payload = {
            "name": "Graffiti",
            "link": "graffiti/index.html",
            "description": "something"
        }
        url = detail_url(self.app1.id)
        self.client.put(url, payload)

        self.app1.refresh_from_db()
        self.assertEqual(self.app1.name, payload['name'])
        self.assertEqual(self.app1.link, payload['link'])
        self.assertEqual(self.app1.description, payload['description'])
