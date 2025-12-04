from __future__ import annotations

from rest_framework import serializers

from tasks.models import Task
from .models import Comment, CommentAttachment


class CommentAttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = CommentAttachment
        fields = ("id", "file", "filename", "created_at")
        read_only_fields = ("id", "filename", "created_at")


class CommentSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(source="task", queryset=Task.objects.all(), write_only=True)
    attachments = CommentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "task", "task_id", "user", "text", "attachments", "created_at")
        read_only_fields = ("id", "task", "created_at")

    def create(self, validated_data):
        # user should be set from request context
        user = self.context["request"].user
        comment = Comment.objects.create(user=user, **validated_data)
        return comment
