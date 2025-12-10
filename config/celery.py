import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("kanban-manager")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Ensure shared tasks in non-app modules (e.g., core.email) are registered
import core.email  # noqa: E402,F401


@app.task(bind=True)
def healthcheck(self):
    return "healthy"
