from django.contrib import admin

from .models import Project, ProjectMember


class ProjectMemberInline(admin.TabularInline):
	model = ProjectMember
	extra = 0
	autocomplete_fields = ("user",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ("name", "team", "archived", "created_at")
	list_filter = ("archived", "team")
	search_fields = ("name", "team__name")
	inlines = (ProjectMemberInline,)


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
	list_display = ("project", "user", "role", "joined_at")
	list_filter = ("role",)
	search_fields = ("project__name", "user__email")
