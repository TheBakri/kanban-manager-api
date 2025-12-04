from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import ProjectMember
from projects.permissions import IsProjectManager, IsProjectMember

from .models import Board, BoardList
from .serializers import BoardSerializer, ListSerializer
from .services import reorder_board_lists


class BoardViewSet(viewsets.ModelViewSet):
	serializer_class = BoardSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		return (
			Board.objects.filter(project__members__user=self.request.user)
			.select_related("project")
			.prefetch_related("lists")
			.distinct()
		)

	def get_permissions(self):
		if self.action in ("list", "retrieve"):
			classes = (permissions.IsAuthenticated, IsProjectMember)
		else:
			classes = (permissions.IsAuthenticated, IsProjectManager)
		return [permission() for permission in classes]

	def perform_create(self, serializer):
		project = serializer.validated_data.get("project")
		if not ProjectMember.objects.filter(
			project=project,
			user=self.request.user,
			role=ProjectMember.RoleChoices.MANAGER,
		).exists():
			raise PermissionDenied("Only project managers can create boards.")
		serializer.save()

	def perform_update(self, serializer):
		project = serializer.validated_data.get("project") or self.get_object().project
		if not ProjectMember.objects.filter(
			project=project,
			user=self.request.user,
			role=ProjectMember.RoleChoices.MANAGER,
		).exists():
			raise PermissionDenied("Only project managers can update boards.")
		serializer.save()


class ListViewSet(viewsets.ModelViewSet):
	serializer_class = ListSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = BoardList.objects.filter(board__project__members__user=self.request.user).select_related("board")
		board_id = self.request.query_params.get("board")
		if board_id:
			queryset = queryset.filter(board_id=board_id)
		return queryset.distinct()

	def get_permissions(self):
		if self.action in ("list", "retrieve"):
			classes = (permissions.IsAuthenticated, IsProjectMember)
		else:
			classes = (permissions.IsAuthenticated, IsProjectManager)
		return [permission() for permission in classes]

	def perform_create(self, serializer):
		board = serializer.validated_data.get("board")
		if not ProjectMember.objects.filter(
			project=board.project,
			user=self.request.user,
			role=ProjectMember.RoleChoices.MANAGER,
		).exists():
			raise PermissionDenied("Only project managers can create lists.")
		serializer.save()

	def perform_update(self, serializer):
		board = serializer.validated_data.get("board") or self.get_object().board
		if not ProjectMember.objects.filter(
			project=board.project,
			user=self.request.user,
			role=ProjectMember.RoleChoices.MANAGER,
		).exists():
			raise PermissionDenied("Only project managers can update lists.")
		serializer.save()


class ReorderListsView(APIView):
	permission_classes = (permissions.IsAuthenticated, IsProjectManager)

	def post(self, request, board_id):
		board = get_object_or_404(Board, pk=board_id)
		self.check_object_permissions(request, board)
		order = request.data.get("order")
		if not isinstance(order, list) or not order:
			raise ValidationError({"order": "Provide a non-empty list of list ids."})
		try:
			reorder_board_lists(board=board, ordered_ids=[int(item) for item in order])
		except (ValueError, DjangoValidationError) as exc:
			raise ValidationError(str(exc)) from exc
		serializer = BoardSerializer(board, context={"request": request})
		return Response(serializer.data, status=status.HTTP_200_OK)
