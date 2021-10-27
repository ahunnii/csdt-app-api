from rest_framework import serializers

from core.models import Tag, Project, Application, Software


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id', )


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for applications"""

    class Meta:
        model = Application
        fields = ('id', 'name', 'link', 'description')
        read_only_fields = ('id',)


class SoftwareSerializer(serializers.ModelSerializer):
    """Serializer for software objects"""
    class Meta:
        model = Software
        fields = ('id', 'name', 'default_file', 'application', 'description')
        read_only_fields = ('id',)


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for project objects"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Project
        fields = ('id', 'title', 'application', 'data', 'thumbnail',
                  'description', 'created_date', 'modified_date', 'tags',
                  'modified_date_history', 'modified_data_history',
                  'modified_thumbnail_history')
        read_only_fields = ('id',)


class ProjectDetailSerializer(ProjectSerializer):
    """Serializer for Project details"""
    tags = TagSerializer(many=True, read_only=True)


class ProjectImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes"""

    class Meta:
        model = Project
        fields = ('id', 'thumbnail')
        read_only_fields = ('id',)
