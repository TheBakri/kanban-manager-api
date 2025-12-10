from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.tasks import send_welcome_email
from .tasks import notify_profile_updated

User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        send_welcome_email.delay(user_id=str(instance.id))
    else:
        notify_profile_updated.delay(user_id=str(instance.id))
