import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Comment, CommentAttachment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def log_comment_activity(sender, instance, created, **kwargs):
    if created:
        logger.info("Comment %s created on task %s by user %s", instance.id, instance.task_id, instance.user_id)
    else:
        logger.info("Comment %s updated", instance.id)


@receiver(post_save, sender=CommentAttachment)
def log_comment_attachment(sender, instance, created, **kwargs):
    if created:
        logger.info("Attachment %s added to comment %s", instance.id, instance.comment_id)
