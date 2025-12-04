from django.shortcuts import get_object_or_404
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

