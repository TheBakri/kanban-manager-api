from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet

router = DefaultRouter()
router.register(r"", CommentViewSet, basename="comments")

app_name = "comments"

urlpatterns = [
    path("", include(router.urls)),
]
