from django.urls import path, include
from rest_framework.routers import DefaultRouter

from project import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('applications', views.ApplicationViewSet)
router.register('softwares', views.SoftwareViewSet)
router.register('projects', views.ProjectViewSet)
router.register('tools', views.ToolViewSet)

app_name = 'project'

urlpatterns = [
    path('', include(router.urls))
]
