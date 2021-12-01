import tempfile
import os
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Project, Application, Software, Tag, Tool

from project.serializers import SoftwareSerializer, SoftwareDetailSerializer



SOFTWARE_URL = reverse('project:software-list')


def detail_url(id):
    """Return project detail URL"""
    return reverse('project:software-detail', args=[id])


def data_upload_url(id):
    """Return URL for project thumbnail upload"""
    return reverse('project:software-upload-data', args=[id])


def sample_software(**params):
    """Create and return a sample software"""
    defaults = {
        'name': 'Adinkra Animations',
        'tool': 0,
        'application': 1,
    }
    defaults.update(params)
    return Software.objects.create(**defaults)


def sample_application(name='Test', **params):
    """Create and return a sample application"""

    defaults = {
        'name': name,
        'link': f'{name}/index.html',
        'description': 'Text'
    }
    defaults.update(params)
    return Application.objects.create(**defaults)


class PublicSoftwareApiTests(TestCase):
    """Test unauthenticated project api access"""

    def setUp(self):
        self.client = APIClient()
        self.tool = Tool.objects.create(name='Cornrow Curves')
        self.app = sample_application()
        self.software = sample_software(tool=self.tool, application=self.app)


    def test_retrieve_software(self):
        """Test retrieving a list of software"""
        res = self.client.get(SOFTWARE_URL)

        software = Software.objects.all()
        serializer = SoftwareSerializer(software, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_unauthenticated_create_software(self):
        """Test that unauthenticated users cannot create new software"""
        payload = {'name':"Adinkra Grapher", 'tool':self.tool, 'application':self.app}
        res = self.client.post(SOFTWARE_URL, payload=payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unable_to_update_software(self):
        """Test that unauthenticated users cannot update software"""
        payload = { 'name': "Adinkra Grapher 2"}
        url = detail_url(self.software.id)
        res = self.client.patch(url, payload)

        self.software.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(self.software.name, payload['name'])


class StaffSoftwareApiTests(TestCase):
    """Test staff software api access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test',
            'test@csdt.org',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.tool = Tool.objects.create(name='Cornrow Curves')
        self.application = sample_application()

    def test_retrieve_software(self):
        """Test retrieving a list of software"""
        sample_software(tool=self.tool, application=self.application, name="A")
        sample_software(tool=self.tool, application=self.application, name="B")

        res = self.client.get(SOFTWARE_URL)

        software = Software.objects.all().order_by('-id')
        serializer = SoftwareSerializer(software, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_software_detail(self):
        """Test viewing project detail"""
        software =  sample_software(tool=self.tool, application=self.application, name="C")

        url = detail_url(software.id)
        res = self.client.get(url)

        serializer = SoftwareDetailSerializer(software)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_software(self):
        """Test creating basic software"""
        payload = {
            'name':"Adinkra Math",
            'tool':self.tool.pk,
            'default_file': "",
            'application':self.application.pk
        }
        res = self.client.post(SOFTWARE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        software = Software.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'application':
                self.assertEqual(payload['application'],
                                 getattr(software, 'application').pk)
            elif key == 'tool':
                self.assertEqual(payload['tool'],
                                 getattr(software, 'tool').pk)
            else:
                self.assertEqual(payload[key], getattr(software, key))


    def test_partial_update_software(self):
        """Test updating a project with patch."""
        software =  sample_software(tool=self.tool, application=self.application, name="D")
        payload = {'name': 'Patched Software'}
        url = detail_url(software.id)
        self.client.patch(url, payload)

        software.refresh_from_db()
        self.assertEqual(software.name, payload['name'])

    def test_full_update_software(self):
        """Test updating a project with put."""
        software =  sample_software(tool=self.tool, application=self.application, name="E")
        tool = Tool.objects.create(name="New Tool")
        payload = {
            'name': 'Full updated project',
            'tool': tool.pk,
            'application': self.application.pk,
        }
        url = detail_url(software.id)
        self.client.put(url, payload)

        software.refresh_from_db()
        self.assertEqual(software.name, payload['name'])
        self.assertEqual(software.tool.pk, payload['tool'])


class SoftwareDataUploadTests(TestCase):
    """Test file uploads to a software"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'dataTest',
            'dataTest@csdt.org',
            'datapass'
        )

        self.client.force_authenticate(self.user)
        self.application = sample_application()
        self.tool = Tool.objects.create(name='Cornrow Curves')
        self.software = sample_software(tool=self.tool, application=self.application, name="Data Upload")

    def tearDown(self):
        self.software.default_file.delete()

    def test_upload_data_to_software(self):
        """Test uploading an data to a software"""
        url = data_upload_url(self.software.id)
        project_file = settings.BASE_DIR / 'samples/data.xml'
        with open(project_file, encoding="utf-8") as tdf:
            res = self.client.post(url, {'default_file': tdf})

        self.software.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('default_file', res.data)
        self.assertTrue(os.path.exists(self.software.default_file.path))

    def test_upload_data_bad_request(self):
        """Test uploading an invalid file"""
        url = data_upload_url(self.software.id)
        res = self.client.post(
            url,
            {'default_file': 'test'},
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
