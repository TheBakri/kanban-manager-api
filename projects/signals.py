import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project, ProjectMember

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Project)
def log_project_activity(sender, instance, created, **kwargs):
    if created:
        logger.info("Project %s created for team %s", instance.name, instance.team_id)
    else:
        logger.info("Project %s updated", instance.id)


@receiver(post_save, sender=ProjectMember)
def log_project_member(sender, instance, created, **kwargs):
    if created:
        logger.info("User %s added to project %s as %s", instance.user_id, instance.project_id, instance.role)
