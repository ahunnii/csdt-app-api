from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(username='test', email='test@csdt.org', password='testpass'):
    """Create a test user"""
    return get_user_model().objects.create_user(username, email, password)


def sample_application(name="CSnap",
                       link="/static/csnap/index.html",
                       description="Base application"):
    """Create a test application"""
    return models.Application.objects.create(name, link, description)


class ModelTests(TestCase):

    def test_create_new_user_successful(self):
        """Test creating a new user with an email and username is successful"""
        email = "test@csdt.org"
        username = "test"
        password = "Test2021!"
        user = get_user_model().objects.create_user(
            email=email,
            username=username,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "test@CSDT.ORG"
        user = get_user_model().objects.create_user(
            email,
            'test',
            'something124'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_email_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                'test',
                'something124'
            )

    def test_new_user_username_invalid_username(self):
        """Test creating user with no username raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                'test@csdt.org',
                None,
                'something124'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'dev@csdt.org',
            'dev',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(name='Adinkra')

        self.assertEqual(str(tag), tag.name)

    def test_application_str(self):
        """Test the application string representation"""
        app = models.Application.objects.create(
            name="CSnap",
            link='something',
            description='Something'
        )

        self.assertEqual(str(app), app.name)

    def test_software_str(self):
        """Test the tool string representation"""
        app = models.Application.objects.create(
            name="CSnap",
            link='something',
            description='Something'
        )
        tool = models.Tool.objects.create(
            name="Adinkra"
        )
        software = models.Software.objects.create(
            name="Adinkra Animations",
            tool=tool,
            default_file="Default data to load",
            application=app
        )

        self.assertEqual(str(software), software.name)

    def test_project_str(self):
        """Test the project string representation"""
        app = models.Application.objects.create(
            name="CSnap",
            link='something',
            description='Something'
        )
        project = models.Project.objects.create(
            owner=sample_user(),
            title="Cool Adinkra Project",
            application=app,
            data="Some random project data string",
            thumbnail="Some random image string"
        )

        self.assertEqual(str(project), project.title)

    @patch('uuid.uuid4')
    def test_project_img_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-img-uuid'
        mock_uuid.return_value = uuid
        file_path = models.project_image_file_path(None, 'testimg.jpg')

        exp_path = f'uploads/project/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
