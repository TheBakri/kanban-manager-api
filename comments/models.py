from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from tasks.models import Task


class Comment(models.Model):
	task = models.ForeignKey(Task, related_name="comments", on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="comments", on_delete=models.SET_NULL, null=True)
	text = models.TextField()
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ("-created_at", "id")

	def __str__(self):
		return f"Comment {self.id} on task {self.task_id}"


class CommentAttachment(models.Model):
	comment = models.ForeignKey(Comment, related_name="attachments", on_delete=models.CASCADE)
	file = models.FileField(upload_to="comment_attachments/%Y/%m/%d")
	filename = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	def save(self, *args, **kwargs):
		if not self.filename and self.file:
			self.filename = getattr(self.file, "name", "")
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.filename} ({self.comment_id})"

