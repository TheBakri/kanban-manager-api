from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from boards.models import Board, BoardList
from notifications.tasks import (
    send_task_assigned_email,
    send_task_due_soon_email,
    send_welcome_email,
)
from projects.models import Project, ProjectMember
from tasks.models import Task
from teams.models import Team, TeamMember

User = get_user_model()


def _build_task(user: User, due_date=None) -> Task:
    team = Team.objects.create(name="Team Alpha", description="", created_by=user)
    TeamMember.objects.create(team=team, user=user, role=TeamMember.RoleChoices.OWNER)
    project = Project.objects.create(team=team, name="Project A")
    ProjectMember.objects.create(project=project, user=user, role=ProjectMember.RoleChoices.MANAGER)
    board = Board.objects.create(project=project, name="Dev Board")
    board_list = BoardList.objects.filter(board=board).first()
    if not board_list:
        board_list = BoardList.objects.create(board=board, name="Todo", position=1)
    return Task.objects.create(
        project=project,
        board_list=board_list,
        title="Task 1",
        position=1,
        assigned_to=user,
        due_date=due_date,
    )


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="test@example.com",
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class EmailTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="tasks@example.com", password="StrongPass123")

    def test_welcome_email(self):
        send_welcome_email.delay(self.user.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Welcome", mail.outbox[0].subject)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_task_assignment_email(self):
        task = _build_task(self.user)
        mail.outbox.clear()

        send_task_assigned_email.delay(task.id)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("assigned", mail.outbox[0].subject.lower())
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_task_due_soon_email(self):
        due_date = timezone.now() + timedelta(hours=12)
        task = _build_task(self.user, due_date=due_date)
        mail.outbox.clear()

        send_task_due_soon_email.delay(task.id)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("due soon", mail.outbox[0].subject.lower())
        self.assertIn(self.user.email, mail.outbox[0].to)
