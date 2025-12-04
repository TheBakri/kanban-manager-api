from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Project, ProjectMember
from teams.models import Team, TeamMember
from boards.models import Board, BoardList
from tasks.models import Task
from .models import Comment

User = get_user_model()


class CommentsApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(email="commenter@example.com", password="StrongPass123")
		self.team = Team.objects.create(name="Team Alpha", description="", created_by=self.user)
		TeamMember.objects.create(team=self.team, user=self.user, role=TeamMember.RoleChoices.OWNER)
		self.project = Project.objects.create(team=self.team, name="Project A")
		ProjectMember.objects.create(project=self.project, user=self.user, role=ProjectMember.RoleChoices.MANAGER)
		self.board = Board.objects.create(project=self.project, name="Comments Board")
		self.list_todo = BoardList.objects.filter(board=self.board).first()
		self.client.force_authenticate(self.user)

	def test_create_comment_and_list_by_task(self):
		task = Task.objects.create(project=self.project, board_list=self.list_todo, title="Task X", position=1)
		url = reverse("comments:comments-list")
		payload = {"task_id": task.id, "text": "This is a comment"}
		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		comment = Comment.objects.get(text="This is a comment")
		self.assertEqual(comment.task_id, task.id)

		# list comments for task
		list_url = reverse("comments:comments-list") + f"task/{task.id}/"
		response = self.client.get(list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertGreaterEqual(len(response.data), 1)

