from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from tasks.models import Task
from .tasks import send_task_assigned_notification, send_task_due_soon_notification


@receiver(post_save, sender=Task)
def task_assignment_notification(sender, instance, created, **kwargs):
    # When a task is created with assigned_to, notify the user
    user = getattr(instance, "assigned_to", None)
    if created and user:
        # Fire async task to create notification (in tests Celery runs eagerly)
        send_task_assigned_notification.delay(user_id=user.id, task_data={"title": instance.title, "id": instance.id})


@receiver(pre_save, sender=Task)
def task_due_and_assignment_changed(sender, instance, **kwargs):
    # On update, detect assignment change or due date close and notify
    if not instance.pk:
        return
    try:
        old = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        return
    # assignment changed
    old_user = getattr(old, "assigned_to", None)
    new_user = getattr(instance, "assigned_to", None)
    if old_user is None and new_user is not None:
        send_task_assigned_notification.delay(user_id=new_user.id, task_data={"title": instance.title, "id": instance.id})
    elif old_user is not None and new_user is not None and old_user.id != new_user.id:
        send_task_assigned_notification.delay(user_id=new_user.id, task_data={"title": instance.title, "id": instance.id})

    # If due_date is being set or changed to near (optional - here we check if date exists and is within X hours),
    # we only enqueue a notification if due_date is within next 24 hours for the assigned user.
    due_old = getattr(old, "due_date", None)
    due_new = getattr(instance, "due_date", None)
    # Only do check when assigned_to exists
    if getattr(instance, "assigned_to", None) and due_new and due_new != due_old:
        time_diff = due_new - timezone.now()
        # if due date within 24 hours, notify
        from datetime import timedelta

        if time_diff <= timedelta(hours=24):
            user_id = instance.assigned_to.id
            send_task_due_soon_notification.delay(user_id=user_id, task_data={"title": instance.title, "due_date": str(due_new)})
