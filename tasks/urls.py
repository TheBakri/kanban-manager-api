from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, move_task_view, reorder_tasks_view

router = DefaultRouter()
router.register(r"", TaskViewSet, basename="tasks")

app_name = "tasks"

urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/move/", move_task_view, name="task-move"),
    path("list/<int:list_pk>/reorder/", reorder_tasks_view, name="tasks-reorder"),
]
