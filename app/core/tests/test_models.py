from django.test import TestCase
from django.contrib.auth import get_user_model


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
