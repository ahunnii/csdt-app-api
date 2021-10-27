from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, \
                                       IsAuthenticated

from django.core.exceptions import PermissionDenied

from core.models import Tag, Project, Application, Software

from project import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Return objects for only authenticated users"""
        return self.queryset.all().order_by('-name')

    def perform_create(self, serializer):
        """Create a new tag only if user is staff"""
        if not self.request.user.is_staff:
            raise PermissionDenied()

        serializer.save()


class ProjectViewSet(viewsets.ModelViewSet):
    """Manage projects in the database"""
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Retrieve the projects for the authenticated user"""
        return self.queryset.filter(owner=self.request.user)

    def get_serializer_class(self):
        """Return the appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.ProjectDetailSerializer

        return self.serializer_class


class ApplicationViewSet(viewsets.ModelViewSet):
    """Manage applications in the database"""
    serializer_class = serializers.ApplicationSerializer
    queryset = Application.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Retrieve the applications for the authenticated user"""
        return self.queryset.order_by('-name')


class SoftwareViewSet(viewsets.ModelViewSet):
    """Manage software in the database"""
    serializer_class = serializers.SoftwareSerializer
    queryset = Software.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Retrieve the software for the authenticated user"""
        return self.queryset.order_by('-name')
