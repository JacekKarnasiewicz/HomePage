from django.conf import settings
from django.contrib.auth.hashers import get_hasher, make_password
from django.db import models


class PasswordManager(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	site_name = models.CharField(max_length=32, unique=True)
	site_url = models.URLField(max_length=128)
	login_name = models.CharField(max_length=32)
	login_password = models.CharField(max_length=128)

	def encode_login_password(self):
		return make_password(self.login_password)

	def decode_login_password(self):
		password_hasher = get_hasher()
		return password_hasher.safe_summary(self.login_password)

	def save(self, *args, **kwargs):
		# self.login_password = self.encode_login_password()
		super().save(*args, **kwargs)
