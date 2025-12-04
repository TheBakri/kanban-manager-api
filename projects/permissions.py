from __future__ import annotations

from rest_framework.permissions import BasePermission

from .models import Project, ProjectMember


def _extract_project(obj):
    if isinstance(obj, Project):
        return obj
    if hasattr(obj, "project"):
        return obj.project
    if hasattr(obj, "board"):
        board = getattr(obj, "board")
        return getattr(board, "project", None)
    return None


class IsProjectMember(BasePermission):
    message = "You must be a project member."

    def has_object_permission(self, request, view, obj):
        project = _extract_project(obj)
        if not project or not request.user.is_authenticated:
            return False
        return ProjectMember.objects.filter(project=project, user=request.user).exists()


class IsProjectManager(BasePermission):
    message = "You must be a project manager."

    def has_object_permission(self, request, view, obj):
        project = _extract_project(obj)
        if not project or not request.user.is_authenticated:
            return False
        return ProjectMember.objects.filter(
            project=project,
            user=request.user,
            role=ProjectMember.RoleChoices.MANAGER,
        ).exists()
