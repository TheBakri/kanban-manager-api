from django.contrib import admin

from .models import Board, BoardList


class BoardListInline(admin.TabularInline):
	model = BoardList
	extra = 0


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
	list_display = ("name", "project", "created_at")
	search_fields = ("name", "project__name")
	inlines = (BoardListInline,)


@admin.register(BoardList)
class BoardListAdmin(admin.ModelAdmin):
	list_display = ("name", "board", "position")
	list_editable = ("position",)
	ordering = ("board", "position")
