import base64

from Crypto import Random
from Crypto.Cipher import AES

from django.conf import settings
from django.contrib.auth.hashers import get_hasher, make_password
from django.db import models


class PasswordManager(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	site_name = models.CharField(max_length=32, unique=True)
	site_url = models.URLField(max_length=128)
	login_name = models.CharField(max_length=32)
	login_password = models.CharField(max_length=128)

	# encryption
	# secret_key = settings.CIPHER_SECRET_KEY
	secret_key = settings.SECRET_KEY
	block_size = AES.block_size

	def encrypt_login_password(self):
		cls = self.__class__
		raw = self.pad(self.login_password)
		iv = Random.new().read(cls.block_size)
		cipher = AES.new(cls.secret_key.encode(encoding='utf-8', errors='strict'), AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt_login_password(self):
		cls = self.__class__
		# try decode
		enc = base64.b64decode(self.login_password)
		iv = enc[:cls.block_size]
		cipher = AES.new(cls.secret_key, AES.MODE_CBC, iv)
		return cls.unpad(cipher.decrypt(enc[cls.block_size:]))

	def pad(self, s):
		cls = self.__class__
		return (s + (cls.block_size - len(s) % cls.block_size) *
				chr(cls.block_size - len(s) % cls.block_size))

	@staticmethod
	def unpad(s):
		return s[:-ord(s[len(s) - 1:])]

	def save(self, *args, **kwargs):
		self.login_password = self.encrypt_login_password()
		super().save(*args, **kwargs)
