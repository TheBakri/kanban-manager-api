from django.contrib import admin

from .models import Task, Subtask, Attachment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "project", "board_list", "assigned_to", "priority", "position", "status")
	list_filter = ("priority", "status")
	search_fields = ("title", "description")


@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "task", "completed", "position")
	list_filter = ("completed",)
	search_fields = ("title",)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
	list_display = ("id", "filename", "task", "created_at")
