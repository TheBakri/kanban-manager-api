import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Task, Subtask, Attachment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Task)
def log_task_activity(sender, instance, created, **kwargs):
    if created:
        logger.info("Task %s created in project %s", instance.title, instance.project_id)
    else:
        logger.info("Task %s updated", instance.id)


@receiver(pre_save, sender=Task)
def detect_task_move(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        return
    if old.board_list_id != instance.board_list_id:
        logger.info("Task %s moved from list %s to %s", instance.id, old.board_list_id, instance.board_list_id)


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
