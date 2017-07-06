from rest_framework.serializers import (Field, HyperlinkedIdentityField,
	ModelSerializer, SerializerMethodField)

from ..models import PasswordManager


# List
class PasswordManagerListSerializer(ModelSerializer):
	detail = HyperlinkedIdentityField(
		view_name='password_manager:api:retrieve',
		lookup_field='site_name')

	class Meta:
		model = PasswordManager
		fields = ('detail', 'site_name', 'site_url')


# Retrieve
class PasswordManagerRetrieveSerializer(ModelSerializer):
	login_password = SerializerMethodField()

	class Meta:
		model = PasswordManager
		fields = ('site_name', 'site_url', 'login_name', 'login_password')

	def get_login_password(self, obj):
		return obj.decrypt_login_password()


# Create
class PasswordManagerCreateSerializer(ModelSerializer):

	class Meta:
		model = PasswordManager
		fields = ('site_name', 'site_url', 'login_name', 'login_password')


# Custom field
class LoginPasswordField(Field):
	def get_attribute(self, obj):
		# We pass the object instance onto `to_representation`,
		# not just the field attribute.
		return obj

	def to_representation(self, obj):
		"""
		Serialize the object's class name.
		"""
		return obj.decrypt_login_password()

	def to_internal_value(self, data):
		return data


# Update
class PasswordManagerUpdateSerializer(ModelSerializer):
	login_password = LoginPasswordField()

	class Meta:
		model = PasswordManager
		fields = ('site_name', 'site_url', 'login_name', 'login_password')


# Destroy
class PasswordManagerDestroySerializer(ModelSerializer):

	class Meta:
		model = PasswordManager
		fields = ('site_name', 'site_url', 'login_name', 'login_password')
