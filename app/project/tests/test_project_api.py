from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Project, Application

from project.serializers import ProjectSerializer


PROJECTS_URL = reverse('project:project-list')


def sample_project(user, **params):
    """Create and return a sample project"""

    defaults = {
        'title': 'Cool Project',
        'application': 1,
        'data': 'Sample data',
        'thumbnail': 'Sample thumbnail',
    }
    defaults.update(params)

    return Project.objects.create(owner=user, **defaults)


def sample_application(**params):
    """Create and return a sample application"""

    defaults = {
        'name': "Test",
        'link': 'Link',
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
