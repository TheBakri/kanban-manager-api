from __future__ import annotations

from django.db.models import Max
from rest_framework import serializers

from projects.models import Project

from .models import Board, BoardList


class ListSerializer(serializers.ModelSerializer):
    board_id = serializers.PrimaryKeyRelatedField(source="board", queryset=Board.objects.all(), write_only=True)

    class Meta:
        model = BoardList
        fields = ("id", "board", "board_id", "name", "position", "created_at", "updated_at")
        read_only_fields = ("id", "board", "created_at", "updated_at")

    def create(self, validated_data):
        board = validated_data["board"]
        if validated_data.get("position") is None:
            next_position = board.lists.aggregate(max_pos=Max("position")).get("max_pos") or 0
            validated_data["position"] = next_position + 1
        return super().create(validated_data)


class BoardSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(source="project", queryset=Project.objects.all())
    project = serializers.CharField(source="project.name", read_only=True)
    lists = ListSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = (
            "id",
            "project",
            "project_id",
            "name",
            "created_at",
            "updated_at",
            "lists",
        )
        read_only_fields = ("id", "project", "created_at", "updated_at", "lists")
