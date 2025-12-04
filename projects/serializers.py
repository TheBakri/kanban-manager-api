from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from teams.models import Team

from .models import Project, ProjectMember
from .services import add_project_member

User = get_user_model()


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name")


class ProjectMemberSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source="user", queryset=User.objects.all(), write_only=True)

    class Meta:
        model = ProjectMember
        fields = ("id", "user", "user_id", "role", "joined_at")
        read_only_fields = ("id", "user", "joined_at")

    def create(self, validated_data):
        project = self.context["project"]
        return add_project_member(project=project, **validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    team_id = serializers.PrimaryKeyRelatedField(source="team", queryset=Team.objects.all())
    team = serializers.CharField(source="team.name", read_only=True)
    members = ProjectMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "team",
            "team_id",
            "name",
            "description",
            "archived",
            "created_at",
            "updated_at",
            "members",
        )
        read_only_fields = ("id", "team", "created_at", "updated_at", "members")

    def validate(self, attrs):
        request = self.context.get("request")
        team = attrs.get("team")
        if not team and self.instance:
            team = self.instance.team
        if request and team:
            if not team.members.filter(user=request.user).exists():
                raise serializers.ValidationError({"team_id": "You must belong to the team."})
        return attrs
