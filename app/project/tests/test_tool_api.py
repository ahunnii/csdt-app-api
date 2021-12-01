from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tool

from project.serializers import ToolSerializer

TOOLS_URL = reverse('project:tool-list')


def detail_url(tool_id):
    """Return tool detail url"""
    return reverse('project:tool-detail', args=[tool_id])


def sample_tool(name):
    """Create and return a sample tool"""
    return Tool.objects.create(name=name)


class PublicToolApiTests(TestCase):
    """Test unauthenticated tool api access"""

    def setUp(self):
        self.client = APIClient()
        self.tool = sample_tool("Adinkra")

    def test_retrieve_tools_unauthenticated(self):
        """Test that unauthenticated users view list of tools"""
        res = self.client.get(TOOLS_URL)

        tools = Tool.objects.all().order_by('-id')
        serializer = ToolSerializer(tools, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_unauthenticated_create_application(self):
        """Test that unauthenticated users cannot create new app"""
        payload = {
            'name': 'Barbershop',
        }
        res = self.client.post(TOOLS_URL, payload=payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unable_to_update_app(self):
        """Test that unauthenticated users cannot update tools"""
        payload = {"name": "Adinkra Pro"}
        url = detail_url(self.tool.id)
        res = self.client.patch(url, payload)

        self.tool.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(self.tool.name, payload['name'])


class PrivateToolApiTests(TestCase):
    """Tests for authenticated users for tool api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "base",
            "base@csdt.org",
            "testpass"
        )
        self.client.force_authenticate(self.user)
        self.tool = sample_tool('Henna')

    def test_unable_to_create_tool(self):
        """Test nonstaff cannot create new tools"""
        payload = {"name": "Graffiti"}
        res = self.client.post(TOOLS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unable_to_update_tool(self):
        """Test nonstaff cannot update tools"""
        payload = {"name": "Test"}
        url = detail_url(self.tool)

        res = self.client.patch(url, payload)
        self.tool.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(self.tool.name, payload['name'])


class StaffToolApiTests(TestCase):
    """Tests for staff members using application api"""

    def setUp(self):
        self.client = APIClient()
        self.staff = get_user_model().objects.create_superuser(
            "admin",
            "admin@csdt.org",
            "testpassword"
        )
        self.client.force_authenticate(self.staff)

        self.tool = sample_tool(name='Skateboarding')

    def test_staff_able_to_create_tool(self):
        """Test staff ability to create new tools"""
        payload = {"name": "New Tool"}
        res = self.client.post(TOOLS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tool = Tool.objects.get(id=res.data['id'])
        self.assertEqual(tool.name, payload['name'])

    def test_partial_update_tool(self):
        """Test staff update to tool with patch"""
        payload = {"name": "Adinkra Pro"}
        url = detail_url(self.tool.id)
        self.client.patch(url, payload)

        self.tool.refresh_from_db()
        self.assertEqual(self.tool.name, payload['name'])

    def test_full_update_application(self):
        """Test staff update to tool with put"""
        payload = {"name": "Graffiti Pro"}
        url = detail_url(self.tool.id)
        self.client.put(url, payload)

        self.tool.refresh_from_db()
        self.assertEqual(self.tool.name, payload['name'])
