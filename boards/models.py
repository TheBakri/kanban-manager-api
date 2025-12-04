from __future__ import annotations

from django.db import models
from django.utils import timezone


DEFAULT_LISTS = ["Backlog", "Todo", "Progress", "Review", "Done"]


class Board(models.Model):
	project = models.ForeignKey("projects.Project", related_name="boards", on_delete=models.CASCADE)
	name = models.CharField(max_length=150)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ("project", "name")
		ordering = ("name",)

	def __str__(self):
		return f"{self.name} ({self.project_id})"


class BoardList(models.Model):
	board = models.ForeignKey(Board, related_name="lists", on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	position = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("position", "id")
		unique_together = ("board", "name")

	def __str__(self):
		return f"{self.name} [{self.board_id}]"
