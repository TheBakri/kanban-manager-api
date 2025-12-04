from __future__ import annotations

from typing import Optional

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Notification

User = get_user_model()


@shared_task(bind=True)
def send_task_assigned_notification(self, user_id: int, task_data: dict):
    # Create a Notification entry for the assigned user and (optionally) send an email later
    user = User.objects.filter(pk=user_id).first()
    if not user:
        return None
    message = f"A new task '{task_data.get('title')}' has been assigned to you."
    notif = Notification.objects.create(user=user, message=message, created_at=timezone.now())
    # Additional external delivery (email, push) hooks could go here
    return notif.id


@shared_task(bind=True)
def send_task_due_soon_notification(self, user_id: int, task_data: dict):
    user = User.objects.filter(pk=user_id).first()
    if not user:
        return None
    message = f"Task '{task_data.get('title')}' is due soon ({task_data.get('due_date')})."
    notif = Notification.objects.create(user=user, message=message, created_at=timezone.now())
    return notif.id
