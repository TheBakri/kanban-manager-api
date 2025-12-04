from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from teams.models import Team, TeamMember
from .models import Project

User = get_user_model()


class ProjectEndpointsTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(email="proj@example.com", password="StrongPass123")
		self.team = Team.objects.create(name="Test Team", description="", created_by=self.user)
		TeamMember.objects.create(team=self.team, user=self.user, role=TeamMember.RoleChoices.OWNER)
		self.client.force_authenticate(self.user)

	def test_create_project(self):
		url = reverse("projects:project-list")
		payload = {"team_id": self.team.id, "name": "API Project", "description": "desc"}
		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Project.objects.count(), 1)

	def test_list_projects(self):
		Project.objects.create(team=self.team, name="P1")
		url = reverse("projects:project-list")
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(len(response.data) >= 1)
