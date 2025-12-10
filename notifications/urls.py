from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationListView, email_preview_view, mark_as_read_view

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications-list"),
    path("<int:pk>/read/", mark_as_read_view, name="notifications-mark-as-read"),
    path("emails/preview/<str:template_slug>/", email_preview_view, name="emails-preview"),
]
