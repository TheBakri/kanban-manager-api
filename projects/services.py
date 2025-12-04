from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import ProjectMember

User = get_user_model()


def add_project_member(*, project, user, role: str = ProjectMember.RoleChoices.MEMBER):
    if not project.team.members.filter(user=user).exists():
        raise ValidationError("User must belong to the team before joining the project.")

    membership, created = ProjectMember.objects.get_or_create(
        project=project,
        user=user,
        defaults={"role": role},
    )
    if not created and membership.role != role:
        membership.role = role
        membership.save(update_fields=["role"])
    return membership


def remove_project_member(*, project, user) -> None:
    try:
        membership = ProjectMember.objects.get(project=project, user=user)
    except ProjectMember.DoesNotExist as exc:
        raise ValidationError("User is not part of this project.") from exc

    if membership.role == ProjectMember.RoleChoices.MANAGER:
        managers = ProjectMember.objects.filter(project=project, role=ProjectMember.RoleChoices.MANAGER).count()
        if managers <= 1:
            raise ValidationError("Cannot remove the last project manager.")

    membership.delete()


