from __future__ import annotations

import logging
from datetime import timedelta
from typing import Optional

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from core.email import send_email
from tasks.models import Task
from .models import Notification

logger = logging.getLogger(__name__)
User = get_user_model()


def _due_soon_cache_key(task: Task) -> str:
    due_ts = int(task.due_date.timestamp()) if task.due_date else "none"
    return f"task-due-soon:{task.id}:{due_ts}"


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_welcome_email(self, user_id: int) -> Optional[str]:
    user = User.objects.filter(pk=user_id).first()
    if not user:
        logger.warning("Welcome email skipped: user not found", extra={"user_id": user_id})
        return None
    if not user.email:
        logger.warning("Welcome email skipped: user missing email", extra={"user_id": user_id})
        return None

    subject = "Welcome to Kanban Manager"
    body = f"Hi {user.get_full_name() or user.email}, welcome aboard!"
    send_email(subject, body, user.email, template="emails/welcome.html", context={"user": user})
    logger.info("Welcome email queued", extra={"user_id": user.id, "email": user.email, "subject": subject})
    return user.email


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_task_assigned_email(self, task_id: int) -> Optional[int]:
    task = Task.objects.select_related("assigned_to").filter(pk=task_id).first()
    if not task:
        logger.warning("Assignment email skipped: task not found", extra={"task_id": task_id})
        return None
    if not task.assigned_to or not task.assigned_to.email:
        logger.warning("Assignment email skipped: missing assignee email", extra={"task_id": task_id})
        return None

    user = task.assigned_to
    subject = f"You have been assigned to '{task.title}'"
    body = (
        f"Hi {user.get_full_name() or user.email},\n\n"
        f"You have been assigned to the task '{task.title}'."
    )
    send_email(
        subject,
        body,
        user.email,
        template="emails/task_assigned.html",
        context={"user": user, "task": task},
    )
    logger.info("Assignment email queued", extra={"task_id": task.id, "user_id": user.id, "email": user.email})
    return task.id


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_task_due_soon_email(self, task_id: int) -> Optional[int]:
    task = Task.objects.select_related("assigned_to").filter(pk=task_id).first()
    if not task:
        logger.warning("Due-soon email skipped: task not found", extra={"task_id": task_id})
        return None
    if not task.assigned_to or not task.assigned_to.email:
        logger.warning("Due-soon email skipped: missing assignee email", extra={"task_id": task_id})
        return None
    if not task.due_date:
        logger.warning("Due-soon email skipped: task missing due date", extra={"task_id": task_id})
        return None

    now = timezone.now()
    due_dt = task.due_date
    if timezone.is_naive(due_dt):
        due_dt = timezone.make_aware(due_dt, timezone.get_current_timezone())

    if due_dt <= now:
        logger.info("Due-soon email skipped: task already past due", extra={"task_id": task.id})
        return None

    cache_key = _due_soon_cache_key(task)
    if not cache.add(cache_key, True, timeout=24 * 60 * 60):
        logger.info("Due-soon email suppressed (already sent recently)", extra={"task_id": task.id})
        return None

    user = task.assigned_to
    due_display = timezone.localtime(due_dt)
    subject = f"Task '{task.title}' is due soon"
    body = (
        f"Hi {user.get_full_name() or user.email},\n\n"
        f"The task '{task.title}' is due on {due_display.strftime('%Y-%m-%d %H:%M %Z')}"
    )
    send_email(
        subject,
        body,
        user.email,
        template="emails/task_due_soon.html",
        context={"user": user, "task": task, "due_display": due_display},
    )
    logger.info("Due-soon email queued", extra={"task_id": task.id, "user_id": user.id, "email": user.email})
    return task.id


@shared_task(bind=True)
def check_due_soon_tasks(self) -> int:
    now = timezone.now()
    window = now + timedelta(hours=24)
    tasks_due = Task.objects.select_related("assigned_to").filter(
        due_date__gt=now,
        due_date__lte=window,
        assigned_to__isnull=False,
    )

    enqueued = 0
    for task in tasks_due:
        due_dt = task.due_date
        if timezone.is_naive(due_dt):
            due_dt = timezone.make_aware(due_dt, timezone.get_current_timezone())
        if due_dt <= now:
            continue
        cache_key = _due_soon_cache_key(task)
        if cache.add(cache_key, True, timeout=24 * 60 * 60):
            send_task_due_soon_email.delay(task.id)
            enqueued += 1
    logger.info("check_due_soon_tasks queued %s due-soon emails", enqueued)
    return enqueued


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
