from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Project, ProjectMember
from teams.models import Team, TeamMember
from boards.models import Board, BoardList
from .models import Task

User = get_user_model()


class TaskApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(email="tasker@example.com", password="StrongPass123")
		self.team = Team.objects.create(name="Team Alpha", description="", created_by=self.user)
		TeamMember.objects.create(team=self.team, user=self.user, role=TeamMember.RoleChoices.OWNER)
		self.project = Project.objects.create(team=self.team, name="Project A")
		ProjectMember.objects.create(project=self.project, user=self.user, role=ProjectMember.RoleChoices.MANAGER)
		self.board = Board.objects.create(project=self.project, name="Dev Board")
		self.list_todo = BoardList.objects.filter(board=self.board).first()
		self.list_progress = BoardList.objects.filter(board=self.board).last()
		self.client.force_authenticate(self.user)

	def test_task_creation_sets_default_position_and_status(self):
		url = reverse("tasks:tasks-list")
		payload = {
			"project_id": self.project.id,
			"board_list_id": self.list_todo.id,
			"title": "Implement feature",
			"description": "Details",
		}
		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		task = Task.objects.get(title="Implement feature")
		self.assertEqual(task.position, 1)
		self.assertEqual(task.status, self.list_todo.name)

	def test_move_task_between_lists_and_reorder(self):
		# create multiple tasks in list_todo
		t1 = Task.objects.create(project=self.project, board_list=self.list_todo, title="Task 1", position=1)
		t2 = Task.objects.create(project=self.project, board_list=self.list_todo, title="Task 2", position=2)
		# move t1 to progress
		move_url = reverse("tasks:task-move", args=[t1.id])
		response = self.client.post(move_url, {"target_list_id": self.list_progress.id}, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		t1.refresh_from_db()
		self.assertEqual(t1.board_list_id, self.list_progress.id)
		self.assertEqual(t1.status, self.list_progress.name)

		# reorder tasks in todo (now only t2 remains)
		reorder_url = reverse("tasks:tasks-reorder", args=[self.list_todo.id])
		response = self.client.post(reorder_url, {"ordered_ids": [t2.id]}, format="json")
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

