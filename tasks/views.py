from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from projects.permissions import IsProjectMember, IsProjectManager
from boards.models import BoardList

from .models import Task
from .serializers import TaskSerializer
from .services import move_task_to_list, reorder_tasks


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().select_related("project", "board_list", "assigned_to").prefetch_related("subtasks", "attachments")
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            permission_classes = (permissions.IsAuthenticated, IsProjectMember)
        else:
            permission_classes = (permissions.IsAuthenticated, IsProjectManager)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Users can only see tasks for projects they are a member of
        return Task.objects.filter(project__members__user=self.request.user).distinct()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
def move_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    target_list_id = request.data.get("target_list_id") or request.query_params.get("target_list_id")
    position = request.data.get("position") or request.query_params.get("position")
    if not target_list_id:
        return Response({"target_list_id": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
    target_list = get_object_or_404(BoardList, pk=target_list_id)
    task = move_task_to_list(task, target_list, int(position) if position is not None else None)
    return Response(TaskSerializer(task, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
def reorder_tasks_view(request, list_pk):
    board_list = get_object_or_404(BoardList, pk=list_pk)
    ordered_ids = request.data.get("ordered_ids")
    if not isinstance(ordered_ids, list) or not ordered_ids:
        return Response({"ordered_ids": "This field must be a list of task ids."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        reorder_tasks(board_list, ordered_ids)
    except Exception as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_204_NO_CONTENT)
from django.shortcuts import render

# Create your views here.
