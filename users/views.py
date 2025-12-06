from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAuthenticated, IsOwner
from .serializers import (
	ChangePasswordSerializer,
	LoginSerializer,
	ProfileUpdateSerializer,
	RegisterSerializer,
	UserSerializer,
)


class RegisterView(generics.CreateAPIView):
	serializer_class = RegisterSerializer
	# Allow unauthenticated users to register. Also explicitly disable
	# authentication for this endpoint so the request won't fail if the
	# client sends an invalid/expired Authorization header.
	permission_classes = (permissions.AllowAny,)
	authentication_classes = []

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		refresh = RefreshToken.for_user(user)
		data = {
			"user": UserSerializer(user, context=self.get_serializer_context()).data,
			"refresh": str(refresh),
			"access": str(refresh.access_token),
		}
		headers = self.get_success_headers(serializer.data)
		return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class LoginView(TokenObtainPairView):
	serializer_class = LoginSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
	permission_classes = (IsAuthenticated, IsOwner)

	def get_object(self):
		return self.request.user

	def get_serializer_class(self):
		if self.request.method in ("GET", "HEAD"):
			return UserSerializer
		return ProfileUpdateSerializer


class ChangePasswordView(APIView):
	permission_classes = (IsAuthenticated,)

	def post(self, request, *args, **kwargs):
		serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
