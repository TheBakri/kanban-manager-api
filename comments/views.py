from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from projects.permissions import IsProjectMember, IsProjectManager
from tasks.models import Task

from .models import Comment
from .serializers import CommentSerializer, CommentAttachmentSerializer


class CommentViewSet(viewsets.ModelViewSet):
	queryset = Comment.objects.all().select_related("task", "user").prefetch_related("attachments")
	serializer_class = CommentSerializer

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			permission_classes = (permissions.IsAuthenticated, IsProjectMember)
		else:
			permission_classes = (permissions.IsAuthenticated, IsProjectMember)
		return [permission() for permission in permission_classes]

	def get_queryset(self):
		# allow listing of comments for tasks within projects user belongs to
		return Comment.objects.filter(task__project__members__user=self.request.user).distinct()

	@action(detail=False, methods=["get"], url_path="task/(?P<task_pk>[^/.]+)")
	def list_for_task(self, request, task_pk=None):
		task = get_object_or_404(Task, pk=task_pk)
		# permission check; IsProjectMember will be enforced via viewset
		comments = self.get_queryset().filter(task=task)
		serializer = self.get_serializer(comments, many=True, context={"request": request})
		return Response(serializer.data)

