from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationListView, mark_as_read_view

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications-list"),
    path("<int:pk>/read/", mark_as_read_view, name="notifications-mark-as-read"),
]
