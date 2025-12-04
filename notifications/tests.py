from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Project, ProjectMember
from teams.models import Team, TeamMember
from boards.models import Board, BoardList
from tasks.models import Task
from .models import Notification

User = get_user_model()


class NotificationsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="notify@example.com", password="StrongPass123")
        self.team = Team.objects.create(name="Team Alpha", description="", created_by=self.user)
        TeamMember.objects.create(team=self.team, user=self.user, role=TeamMember.RoleChoices.OWNER)
        self.project = Project.objects.create(team=self.team, name="Project A")
        ProjectMember.objects.create(project=self.project, user=self.user, role=ProjectMember.RoleChoices.MANAGER)
        self.board = Board.objects.create(project=self.project, name="Notification Board")
        self.list_todo = BoardList.objects.filter(board=self.board).first()
        self.client.force_authenticate(self.user)

    def test_notification_created_on_task_assignment(self):
        # create task and assign to user
        task = Task.objects.create(project=self.project, board_list=self.list_todo, title="Task X", position=1, assigned_to=self.user)
        # celery is eager during tests so the Notification should be created sync
        notif = Notification.objects.filter(user=self.user, message__icontains="assigned").first()
        self.assertIsNotNone(notif)

    def test_list_and_mark_read(self):
        n = Notification.objects.create(user=self.user, message="Test notification")
        url = reverse("notifications:notifications-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data.get("results", response.data)), 1)
        # mark as read
        mark_url = reverse("notifications:notifications-mark-as-read", args=[n.id])
        response = self.client.post(mark_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        n.refresh_from_db()
        self.assertTrue(n.is_read)
from django.test import TestCase

# Create your tests here.
