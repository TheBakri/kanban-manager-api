import logging
from datetime import timedelta

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from notifications.tasks import send_task_assigned_email, send_task_due_soon_email
from .models import Task, Subtask, Attachment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Task)
def log_task_activity(sender, instance, created, **kwargs):
    if created:
        logger.info("Task created", extra={"task_id": instance.id, "project_id": instance.project_id})
    else:
        logger.info("Task updated", extra={"task_id": instance.id})

    # Trigger assignment email on initial creation
    if created and instance.assigned_to:
        send_task_assigned_email.delay(task_id=instance.id)


@receiver(pre_save, sender=Task)
def detect_task_move(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        return
    if old.board_list_id != instance.board_list_id:
        logger.info(
            "Task moved",
            extra={"task_id": instance.id, "from_list": old.board_list_id, "to_list": instance.board_list_id},
        )

    old_assignee = getattr(old, "assigned_to_id", None)
    new_assignee = getattr(instance, "assigned_to_id", None)
    if new_assignee and new_assignee != old_assignee:
        send_task_assigned_email.delay(task_id=instance.id)

    if new_assignee and instance.due_date:
        due_changed = getattr(old, "due_date", None) != instance.due_date
        if due_changed:
            time_diff = instance.due_date - timezone.now()
            if timedelta(seconds=0) < time_diff <= timedelta(hours=24):
                send_task_due_soon_email.delay(task_id=instance.id)


@receiver(post_save, sender=Subtask)
def log_subtask_activity(sender, instance, created, **kwargs):
    if created:
        logger.info("Subtask %s created on task %s", instance.id, instance.task_id)
    else:
        logger.info("Subtask %s updated", instance.id)


@receiver(post_save, sender=Attachment)
def log_attachment_activity(sender, instance, created, **kwargs):
    if created:
        logger.info("Attachment %s added to task %s", instance.id, instance.task_id)
