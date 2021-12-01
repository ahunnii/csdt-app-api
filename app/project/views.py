from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, \
                                       IsAuthenticated

from django.core.exceptions import PermissionDenied

from core.models import Tag, Project, Application, Software, Tool

from project import serializers


class BaseProjectAttrViewSet(viewsets.ModelViewSet):
    """Base viewset for apps and software attributes"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """Return related objects"""
        return self.queryset.all().order_by('-id')

    def perform_create(self, serializer):
        """Create a new object if staff"""
        if not self.request.user.is_staff:
            raise PermissionDenied()
        serializer.save()

    def update(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        return super().update(request, *args, **kwargs)


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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(project__isnull=False)
        return queryset.all().order_by('-name').distinct()

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

    def _params_to_ints(self, qs):
        """Convert a list of string ids to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the projects for the authenticated user"""
        tags = self.request.query_params.get('tags')
        applications = self.request.query_params.get('applications')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if applications:
            application_ids = self._params_to_ints(applications)
            queryset = queryset.filter(application__id__in=application_ids)

        return queryset.filter(owner=self.request.user)

    def get_serializer_class(self):
        """Return the appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.ProjectDetailSerializer
        elif self.action == 'upload_image':
            return serializers.ProjectImageSerializer
        elif self.action == 'upload_data':
            return serializers.ProjectDataSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new project"""
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        """Append latest changes to history arrays for data."""
        project = self.get_object()
        project.modified_date_history.append(project.modified_date)
        project.modified_data_history.append(project.data)
        project.modified_thumbnail_history.append(project.thumbnail)
        project.save()
        return super().update(request, *args, **kwargs)

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

    @action(methods=['POST'], detail=True, url_path='upload-data')
    def upload_data(self, request, pk=None):
        """Upload a project's data to a project"""
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


class ApplicationViewSet(BaseProjectAttrViewSet):
    """Manage applications in the database"""
    serializer_class = serializers.ApplicationSerializer
    queryset = Application.objects.all()


class SoftwareViewSet(BaseProjectAttrViewSet):
    """Manage software in the database"""
    serializer_class = serializers.SoftwareSerializer
    queryset = Software.objects.all()

    def get_serializer_class(self):
        """Return the appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.SoftwareDetailSerializer
        elif self.action == 'upload_data':
            return serializers.SoftwareDataSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-data')
    def upload_data(self, request, pk=None):
        """Upload a software's data to a software"""
        software = self.get_object()
        serializer = self.get_serializer(
            software,
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


class ToolViewSet(BaseProjectAttrViewSet):
    """Manage tools in the database"""
    serializer_class = serializers.ToolSerializer
    queryset = Tool.objects.all()
