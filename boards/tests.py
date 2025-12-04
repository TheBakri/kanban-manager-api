from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Project, ProjectMember
from teams.models import Team, TeamMember
from .models import Board, BoardList

User = get_user_model()


class BoardApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(email="boarder@example.com", password="StrongPass123")
		self.team = Team.objects.create(name="Team Alpha", description="", created_by=self.user)
		TeamMember.objects.create(team=self.team, user=self.user, role=TeamMember.RoleChoices.OWNER)
		self.project = Project.objects.create(team=self.team, name="Project A")
		ProjectMember.objects.create(project=self.project, user=self.user, role=ProjectMember.RoleChoices.MANAGER)
		self.client.force_authenticate(self.user)

	def test_board_creation_creates_default_lists(self):
		url = reverse("boards:board-list")
		payload = {"project_id": self.project.id, "name": "Planning"}
		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		board = Board.objects.get(name="Planning")
		self.assertEqual(board.lists.count(), 5)

	def test_reorder_lists(self):
		board = Board.objects.create(project=self.project, name="Delivery")
		# trigger default lists
		self.assertEqual(board.lists.count(), 5)
		reorder_url = reverse("boards:lists-reorder", args=[board.id])
		order = list(reversed(list(board.lists.values_list("id", flat=True))))
		response = self.client.post(reorder_url, {"order": order}, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		first_list = BoardList.objects.get(id=order[0])
		self.assertEqual(first_list.position, 1)
