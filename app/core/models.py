import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.utils import timezone
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


def project_image_file_path(instance, filename):
    """Generate file path for new project image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/project/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a new user"""
        if not email or not username:
            raise ValueError('Users must have an email address and username')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password):
        """Create and save a new superuser"""
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model. Room to expand with multiple fields"""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=255)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


class Tag(models.Model):
    """Tag to be used for a project"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="", max_length=255)

    def __str__(self):
        return self.name


class Application(models.Model):
    """Application object, i.e CSnap"""
    name = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Software(models.Model):
    """Software object, i.e. Adinkra"""
    name = models.CharField(max_length=255, unique=True)
    default_file = models.CharField(max_length=255)
    application = models.ForeignKey(Application, on_delete=models.DO_NOTHING)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    """Project object"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    title = models.CharField(max_length=255)
    application = models.ForeignKey(Application, on_delete=models.DO_NOTHING)
    data = models.CharField(max_length=255)
    thumbnail = models.ImageField(null=True, upload_to=project_image_file_path)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag')
    modified_date_history = ArrayField(
        models.DateTimeField(),
        default=list
    )
    modified_data_history = ArrayField(
        models.CharField(max_length=255),
        default=list
    )
    modified_thumbnail_history = ArrayField(
        models.CharField(max_length=255),
        default=list
        )

    def __str__(self):
        return self.title
