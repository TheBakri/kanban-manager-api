from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class Project(models.Model):
	team = models.ForeignKey("teams.Team", related_name="projects", on_delete=models.CASCADE)
	name = models.CharField(max_length=150)
	description = models.TextField(blank=True)
	archived = models.BooleanField(default=False)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("-created_at", "name")
		unique_together = ("team", "name")

	def __str__(self):
		return f"{self.name} ({self.team})"


class ProjectMember(models.Model):
	class RoleChoices(models.TextChoices):
		MANAGER = "manager", "Manager"
		MEMBER = "member", "Member"
		VIEWER = "viewer", "Viewer"

	project = models.ForeignKey(Project, related_name="members", on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="project_memberships", on_delete=models.CASCADE)
	role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.MEMBER)
	joined_at = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = ("project", "user")
		ordering = ("project", "user")

	def __str__(self):
		return f"{self.user} -> {self.project} ({self.role})"

	@property
	def is_manager(self):
		return self.role == self.RoleChoices.MANAGER
