from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Board
from .services import ensure_default_lists


@receiver(post_save, sender=Board)
def create_default_lists(sender, instance, created, **kwargs):
    if created:
        ensure_default_lists(instance)
