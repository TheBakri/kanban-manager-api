from __future__ import annotations

from django.db.models import Max
from rest_framework import serializers

from boards.models import BoardList
from projects.models import Project

from .models import Task, Subtask, Attachment
from .services import move_task_to_list


class AttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = Attachment
        fields = ("id", "file", "filename", "created_at")
        read_only_fields = ("id", "filename", "created_at")


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ("id", "title", "description", "completed", "position", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class TaskSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(source="project", queryset=Project.objects.all(), write_only=True)
    board_list_id = serializers.PrimaryKeyRelatedField(source="board_list", queryset=BoardList.objects.all(), write_only=True)
    subtasks = SubtaskSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "project",
            "project_id",
            "board_list",
            "board_list_id",
            "title",
            "description",
            "due_date",
            "assigned_to",
            "priority",
            "status",
            "position",
            "tags",
            "subtasks",
            "attachments",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "project", "board_list", "status", "created_at", "updated_at")

    def validate(self, attrs):
        project = attrs.get("project") or getattr(self.instance, "project", None)
        board_list = attrs.get("board_list") or getattr(self.instance, "board_list", None)
        if project and board_list and board_list.board.project_id != project.id:
            raise serializers.ValidationError({"board_list": "Board list must belong to the project specified."})
        return attrs

    def create(self, validated_data):
        if validated_data.get("position") is None:
            board_list = validated_data["board_list"]
            next_pos = board_list.tasks.aggregate(max_pos=Max("position")).get("max_pos") or 0
            validated_data["position"] = next_pos + 1
        task = super().create(validated_data)
        return task

    def update(self, instance, validated_data):
        # If list is changed, use the service to move and reposition the task
        board_list = validated_data.get("board_list")
        if board_list and board_list != instance.board_list:
            position = validated_data.get("position")
            task = move_task_to_list(instance, board_list, position)
            # Update other fields if provided
            for attr, value in validated_data.items():
                if attr in ("board_list", "position"):
                    continue
                setattr(task, attr, value)
            task.save()
            return task
        return super().update(instance, validated_data)
