from django.contrib import admin
from .models import Comment, CommentAttachment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ("id", "task", "user", "created_at")
	list_filter = ("created_at",)
	search_fields = ("text",)


@admin.register(CommentAttachment)
class CommentAttachmentAdmin(admin.ModelAdmin):
	list_display = ("id", "comment", "filename", "created_at")
	list_filter = ("created_at",)
	search_fields = ("filename",)
