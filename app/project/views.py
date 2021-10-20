from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from django.core.exceptions import PermissionDenied

from core.models import Tag
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
        return self.queryset.order_by('-name')

    def perform_create(self, serializer):
        """Create a new tag only if user is staff"""
        if not self.request.user.is_staff:
            raise PermissionDenied()

        serializer.save()
