from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE)
	message = models.TextField()
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ("-created_at", "-id")

	def __str__(self):
		return f"Notification {self.id} for user {self.user_id}"

