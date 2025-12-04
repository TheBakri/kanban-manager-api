from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from boards.models import BoardList
from projects.models import Project


class Task(models.Model):
	class PriorityChoices(models.TextChoices):
		LOW = "low", "Low"
		MEDIUM = "medium", "Medium"
		HIGH = "high", "High"

	project = models.ForeignKey(Project, related_name="tasks", on_delete=models.PROTECT)
	board_list = models.ForeignKey(BoardList, related_name="tasks", on_delete=models.CASCADE)
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	due_date = models.DateTimeField(null=True, blank=True)
	assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="tasks", on_delete=models.SET_NULL, null=True, blank=True)
	priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
	status = models.CharField(max_length=100, blank=True)
	position = models.PositiveIntegerField(default=0)
	tags = models.JSONField(default=list, blank=True)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("position", "id")

	def save(self, *args, **kwargs):
		# Set status automatically from the list name
		if self.board_list and self.board_list.name:
			self.status = self.board_list.name
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.title} ({self.project_id})"


class Subtask(models.Model):
	task = models.ForeignKey(Task, related_name="subtasks", on_delete=models.CASCADE)
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	completed = models.BooleanField(default=False)
	position = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("position", "id")

	def __str__(self):
		return f"{self.title} ({self.task_id})"


class Attachment(models.Model):
	task = models.ForeignKey(Task, related_name="attachments", on_delete=models.CASCADE)
	file = models.FileField(upload_to="attachments/%Y/%m/%d")
	filename = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	def save(self, *args, **kwargs):
		if not self.filename and self.file:
			self.filename = getattr(self.file, "name", "")
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.filename} ({self.task_id})"
