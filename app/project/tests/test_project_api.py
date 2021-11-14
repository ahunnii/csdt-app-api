import tempfile
import os
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APIClient

from PIL import Image

from core.models import Project, Application, Software, Tag

from project.serializers import ProjectSerializer, ProjectDetailSerializer


PROJECTS_URL = reverse('project:project-list')


def detail_url(project_id):
    """Return project detail URL"""
    return reverse('project:project-detail', args=[project_id])


def image_upload_url(project_id):
    """Return URL for project thumbnail upload"""
    return reverse('project:project-upload-image', args=[project_id])


def data_upload_url(project_id):
    """Return URL for project thumbnail upload"""
    return reverse('project:project-upload-data', args=[project_id])


def sample_tag(name='High School'):
    """Create and return a sample tag"""
    return Tag.objects.create(name=name)


def sample_software(**params):
    """Create and return a sample software"""
    defaults = {
        'name': 'Adinkra',
        'default_file': 'Cool spiral',
        'application': 1,
    }

    defaults.update(params)
    return Software.objects.create(**defaults)


def sample_project(user, **params):
    """Create and return a sample project"""

    defaults = {
        'title': 'Cool Project',
        'application': 1,
    }
    defaults.update(params)

    return Project.objects.create(owner=user, **defaults)


def sample_application(name='Test', **params):
    """Create and return a sample application"""

    defaults = {
        'name': name,
        'link': f'{name}/index.html',
        'description': 'Text'
    }
    defaults.update(params)
    return Application.objects.create(**defaults)


class PublicProjectApiTests(TestCase):
    """Test unauthenticated project api access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(PROJECTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProjectApiTests(TestCase):
    """Test authenticated project api access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test',
            'test@csdt.org',
            'testpass'
        )
        self.client.force_authenticate(self.user)

        self.application = sample_application()

    def test_retrieve_projects(self):
        """Test retrieving a list of projects"""
        sample_project(user=self.user, application=self.application)
        sample_project(user=self.user, application=self.application)

        res = self.client.get(PROJECTS_URL)

        projects = Project.objects.all().order_by('-id')
        serializer = ProjectSerializer(projects, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_projects_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'other',
            'other@csdt.org',
            'otherpass'
        )
        sample_project(user=user2, application=self.application)
        sample_project(user=self.user, application=self.application)

        res = self.client.get(PROJECTS_URL)

        project = Project.objects.filter(owner=self.user)
        serializer = ProjectSerializer(project, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_project_detail(self):
        """Test viewing project detail"""
        project = sample_project(user=self.user, application=self.application)
        project.tags.add(sample_tag())

        url = detail_url(project.id)
        res = self.client.get(url)

        serializer = ProjectDetailSerializer(project)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_project(self):
        """Test creating basic project"""
        payload = {
            'title': 'Adinkra Spirals',
            'application': self.application.pk,
        }

        res = self.client.post(PROJECTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'application':
                self.assertEqual(payload['application'],
                                 getattr(project, 'application').pk)
            else:
                self.assertEqual(payload[key], getattr(project, key))

    def test_create_project_with_tags(self):
        """Test creating project with tags"""
        tag1 = sample_tag(name="Cornrow Curves")
        tag2 = sample_tag(name="High School")
        payload = {
            'title': 'Variable Curves',
            'application': self.application.pk,
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(PROJECTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=res.data['id'])
        tags = project.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_partial_update_project(self):
        """Test updating a project with patch."""
        project = sample_project(user=self.user, application=self.application)
        project.tags.add(sample_tag(name='Update'))
        new_tag = sample_tag(name='New Project')

        payload = {'title': 'Patched Project', 'tags': [new_tag.id]}
        url = detail_url(project.id)
        self.client.patch(url, payload)

        project.refresh_from_db()
        self.assertEqual(project.title, payload['title'])
        tags = project.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_project(self):
        """Test updating a project with put."""
        project = sample_project(user=self.user, application=self.application)
        project.tags.add(sample_tag(name='Full Update'))
        payload = {
            'title': 'Full updated project',
            'application': self.application.pk,
        }
        url = detail_url(project.id)
        self.client.put(url, payload)

        project.refresh_from_db()
        self.assertEqual(project.title, payload['title'])
        self.assertEqual(project.application.pk, payload['application'])
        tags = project.tags.all()
        self.assertEqual(len(tags), 0)

    def test_update_track_history(self):
        """Test updating the history arrays with each project"""
        project = sample_project(user=self.user, application=self.application)
        project.tags.add(sample_tag(name='Challenge'))
        project_file = settings.BASE_DIR / 'samples/data.xml'
        url = detail_url(project.id)
        with open(project_file, encoding="utf-8") as tdf:
            payload = {'data': tdf}
            res = self.client.patch(url, payload)

        project.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(project.modified_date_history), 1)
        self.assertEqual(len(project.modified_data_history), 1)
        self.assertEqual(len(project.modified_thumbnail_history), 1)


class ProjectImageUploadTests(TestCase):
    """Tests with image uploads for projects"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'imageTest',
            'imageTest@csdt.org',
            'imagepass'
        )
        self.client.force_authenticate(self.user)
        self.application = sample_application()
        self.project = sample_project(
            user=self.user,
            application=self.application
        )

    def tearDown(self):
        self.project.thumbnail.delete()

    def test_upload_image_to_project(self):
        """Test uploading an image to a project"""
        url = image_upload_url(self.project.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'thumbnail': ntf}, format='multipart')

        self.project.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('thumbnail', res.data)
        self.assertTrue(os.path.exists(self.project.thumbnail.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.project.id)
        res = self.client.post(
            url,
            {'thumbnail': 'notimage'},
            format='multipart'
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_projects_by_tags(self):
        """Test returning projects with specific tags"""
        project1 = sample_project(
            user=self.user,
            application=self.application,
            title="Adinkra Project"
        )
        project2 = sample_project(
            user=self.user,
            application=self.application,
            title="CC Project"
        )
        tag1 = sample_tag(name='Adinkra')
        tag2 = sample_tag(name='Cornrow Curves JS')
        project1.tags.add(tag1)
        project2.tags.add(tag2)
        project3 = sample_project(
            user=self.user,
            application=self.application,
            title="Henna Project"
        )

        res = self.client.get(
            PROJECTS_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = ProjectSerializer(project1)
        serializer2 = ProjectSerializer(project2)
        serializer3 = ProjectSerializer(project3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_projects_by_application(self):
        """Test returning projects by specific application"""
        application1 = sample_application(
            name="Henna",
            link='henna/index.html'
        )
        application2 = sample_application(
            name="Graffiti",
            link='graffiti/index.html'
        )
        project1 = sample_project(
            user=self.user,
            application=application1,
            title="Henna Project"
        )
        project2 = sample_project(
            user=self.user,
            application=application2,
            title="Graffiti Project"
        )

        res = self.client.get(
            PROJECTS_URL,
            {'applications': application1.pk}
        )

        serializer1 = ProjectSerializer(project1)
        serializer2 = ProjectSerializer(project2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)


class ProjectDataUploadTests(TestCase):
    """Test file uploads to a project"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'dataTest',
            'dataTest@csdt.org',
            'datapass'
        )

        self.client.force_authenticate(self.user)
        self.application = sample_application(name='Wheel')
        self.project = sample_project(
            user=self.user,
            application=self.application
        )

    def tearDown(self):
        self.project.data.delete()

    def test_upload_data_to_project(self):
        """Test uploading an data to a project"""
        url = data_upload_url(self.project.id)
        project_file = settings.BASE_DIR / 'samples/data.xml'
        with open(project_file, encoding="utf-8") as tdf:
            res = self.client.post(url, {'data': tdf})

        self.project.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('data', res.data)
        self.assertTrue(os.path.exists(self.project.data.path))

    def test_upload_data_bad_request(self):
        """Test uploading an invalid file"""
        url = data_upload_url(self.project.id)
        res = self.client.post(
            url,
            {'data': 'test'},
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
