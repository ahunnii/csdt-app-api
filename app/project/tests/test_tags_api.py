from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from project.serializers import TagSerializer


TAGS_URL = reverse('project:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publically available tags API."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_tags(self):
        """Test the retrieved tag list API for public users """
        Tag.objects.create(
            name="CSnap",
            description="Some sort of description"
        )
        Tag.objects.create(
            name="High",
            description="High School projects"
        )
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_tag_login_required(self):
        """Test that login is required for retrieving tags"""
        payload = {'name': 'CSDT', 'description': 'Text'}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            'test',
            'test@csdt.org',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags for authenticated users"""
        Tag.objects.create(
            name="CSnap",
            description="Some sort of description"
        )
        Tag.objects.create(
            name="High",
            description="High School projects"
        )
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Quilting', 'description': 'Quilting projects'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': '', 'description': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tag_not_staff(self):
        """Test with non staff users not allowed to create tags"""
        user2 = get_user_model().objects.create_user(
            'test2',
            'test2@csdt.org',
            'password1233'
        )
        client = APIClient()
        client.force_authenticate(user2)
        payload = {'name': 'CSDT', 'description': 'Test'}
        res = client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
