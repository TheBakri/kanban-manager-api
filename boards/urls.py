from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import BoardViewSet, ListViewSet, ReorderListsView

app_name = "boards"

router = DefaultRouter()
router.register(r"boards", BoardViewSet, basename="board")
router.register(r"lists", ListViewSet, basename="board-list")

urlpatterns = [
    path("", include(router.urls)),
    path("boards/<int:board_id>/lists/reorder/", ReorderListsView.as_view(), name="lists-reorder"),
]
