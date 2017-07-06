from rest_framework.generics import (CreateAPIView, DestroyAPIView,
	ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView)
from rest_framework.permissions import IsAuthenticated

from ..models import PasswordManager

from .permissions import OwnerOnly
from .serializers import (
	PasswordManagerListSerializer,
	PasswordManagerRetrieveSerializer,
	PasswordManagerCreateSerializer,
	PasswordManagerUpdateSerializer,
	PasswordManagerDestroySerializer)


class PasswordManagerListAPIView(ListAPIView):
	serializer_class = PasswordManagerListSerializer
	permission_classes = [IsAuthenticated, OwnerOnly]

	def get_queryset(self, *args, **kwargs):
		return PasswordManager.objects.filter(owner=self.request.user)


class PasswordManagerRetrieveAPIView(RetrieveAPIView):
	serializer_class = PasswordManagerRetrieveSerializer
	lookup_field = 'site_name'
	permission_classes = [IsAuthenticated, OwnerOnly]

	def get_queryset(self, *args, **kwargs):
		return PasswordManager.objects.filter(owner=self.request.user)


class PasswordManagerCreateAPIView(CreateAPIView):
	serializer_class = PasswordManagerCreateSerializer
	permission_classes = [IsAuthenticated]

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class PasswordManagerUpdateAPIView(RetrieveUpdateAPIView):
	serializer_class = PasswordManagerUpdateSerializer
	lookup_field = 'site_name'
	permission_classes = [IsAuthenticated, OwnerOnly]

	def perform_update(self, serializer):
		serializer.save(owner=self.request.user)

	def get_queryset(self, *args, **kwargs):
		return PasswordManager.objects.filter(owner=self.request.user)


class PasswordManagerDestroyAPIView(DestroyAPIView):
	serializer_class = PasswordManagerDestroySerializer
	lookup_field = 'site_name'
	permission_classes = [IsAuthenticated, OwnerOnly]

	def get_queryset(self, *args, **kwargs):
		return PasswordManager.objects.filter(owner=self.request.user)
