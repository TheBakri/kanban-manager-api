from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project, ProjectMember
from .permissions import IsProjectManager, IsProjectMember
from .serializers import ProjectMemberSerializer, ProjectSerializer
from .services import add_project_member, remove_project_member

User = get_user_model()


class ProjectListCreateView(generics.ListCreateAPIView):
	serializer_class = ProjectSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		return (
			Project.objects.filter(members__user=self.request.user)
			.select_related("team")
			.prefetch_related("members__user")
			.distinct()
		)

	def perform_create(self, serializer):
		team = serializer.validated_data.get("team")
		if not team.members.filter(user=self.request.user).exists():
			raise PermissionDenied("You must belong to the team.")
		project = serializer.save()
		add_project_member(
			project=project,
			user=self.request.user,
			role=ProjectMember.RoleChoices.MANAGER,
		)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = ProjectSerializer

	def get_queryset(self):
		return (
			Project.objects.filter(members__user=self.request.user)
			.select_related("team")
			.prefetch_related("members__user")
			.distinct()
		)

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			permission_classes = (permissions.IsAuthenticated, IsProjectMember)
		else:
			permission_classes = (permissions.IsAuthenticated, IsProjectManager)
		return [permission() for permission in permission_classes]


class ProjectMembersView(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get_permissions(self):
		if self.request.method == "GET":
			permission_classes = (permissions.IsAuthenticated, IsProjectMember)
		else:
			permission_classes = (permissions.IsAuthenticated, IsProjectManager)
		return [permission() for permission in permission_classes]

	def get_project(self, request, pk):
		project = get_object_or_404(Project, pk=pk)
		self.check_object_permissions(request, project)
		return project

	def get(self, request, pk):
		project = self.get_project(request, pk)
		serializer = ProjectMemberSerializer(
			project.members.select_related("user"),
			many=True,
			context={"request": request},
		)
		return Response(serializer.data)

	def post(self, request, pk):
		project = self.get_project(request, pk)
		serializer = ProjectMemberSerializer(data=request.data, context={"project": project, "request": request})
		serializer.is_valid(raise_exception=True)
		try:
			membership = serializer.save()
		except DjangoValidationError as exc:
			raise ValidationError(exc.message or str(exc)) from exc
		output = ProjectMemberSerializer(membership, context={"request": request}).data
		return Response(output, status=status.HTTP_201_CREATED)

	def delete(self, request, pk):
		project = self.get_project(request, pk)
		user_id = request.data.get("user_id") or request.query_params.get("user_id")
		if not user_id:
			raise ValidationError({"user_id": "This field is required."})
		user = get_object_or_404(User, pk=user_id)
		try:
			remove_project_member(project=project, user=user)
		except DjangoValidationError as exc:
			raise ValidationError(exc.message or str(exc)) from exc
		return Response(status=status.HTTP_204_NO_CONTENT)
