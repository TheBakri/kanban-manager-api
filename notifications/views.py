from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from types import SimpleNamespace
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
	serializer_class = NotificationSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		return Notification.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def mark_as_read_view(request, pk):
	notification = get_object_or_404(Notification, pk=pk, user=request.user)
	notification.is_read = True
	notification.save(update_fields=["is_read"])
	return Response(NotificationSerializer(notification, context={"request": request}).data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def email_preview_view(request, template_slug: str):
	if not settings.DEBUG:
		raise Http404()

	templates = {
		"welcome": "emails/welcome.html",
		"task_assigned": "emails/task_assigned.html",
		"task_due_soon": "emails/task_due_soon.html",
	}
	template = templates.get(template_slug)
	if not template:
		raise Http404()

	# Sample context for preview purposes only
	user = getattr(request, "user", None)
	sample_user = user if getattr(user, "is_authenticated", False) else SimpleNamespace(
		get_full_name=lambda: "Preview User",
		email="preview@example.com",
	)
	task_sample = SimpleNamespace(title="Sample Task", due_date=None)
	context = {
		"user": sample_user,
		"task": task_sample,
		"due_display": None,
	}
	html = render_to_string(template, context)
	return HttpResponse(html)

