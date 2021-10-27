from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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
        elif self.action == 'upload_image':
            return serializers.ProjectImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new project"""
        serializer.save(owner=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload a thumbnail to a project"""
        project = self.get_object()
        serializer = self.get_serializer(
            project,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ApplicationViewSet(viewsets.ModelViewSet):
    """Manage applications in the database"""
    serializer_class = serializers.ApplicationSerializer
    queryset = Application.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Retrieve the applications for the authenticated user"""
        return self.queryset.order_by('-name')

    def perform_create(self, serializer):
        """Create a new project"""
        serializer.save()


class SoftwareViewSet(viewsets.ModelViewSet):
    """Manage software in the database"""
    serializer_class = serializers.SoftwareSerializer
    queryset = Software.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Retrieve the software for the authenticated user"""
        return self.queryset.order_by('-name')
