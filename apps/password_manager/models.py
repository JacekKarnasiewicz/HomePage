import base64
import datetime

# pycryptodome
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
	login_password = models.CharField(
		max_length=128,
		verbose_name='Login password',
		help_text="Password should have at least one lower and upper case letter, at least one number and one special character(e.g. !?.@#$).")

	# encryption key
	# We shouldn't keep SECRET encryption key here - it should be secret!(e.g. environment variable)
	# It's for fast installation from git, and easier way to review and test code
	secret_key = "d5gnOM2V!|E1[TxhHi]@I'eDst*Ha[zq"
	secret_key_link = 'GY;g\x0b@)D#6^;lD4@\x0bT?&E1Yh-hcq]U\x0c\x0b'
	block_size = AES.block_size

	def encrypt_login_password(self):
		cls = self.__class__
		raw = self.pad(self.login_password).encode(encoding='utf-8', errors='strict')
		iv = Random.new().read(cls.block_size)
		cipher = AES.new(cls.secret_key.encode(encoding='utf-8', errors='strict'), AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt_login_password(self):
		cls = self.__class__
		enc = base64.b64decode(self.login_password)
		iv = enc[:cls.block_size]
		cipher = AES.new(cls.secret_key.encode(encoding='utf-8', errors='strict'), AES.MODE_CBC, iv)
		bytes_string = cls.unpad(cipher.decrypt(enc[cls.block_size:]))
		return bytes_string.decode(encoding='utf-8')

	def pad(self, s):
		cls = self.__class__
		return (s + (cls.block_size - len(s) % cls.block_size) *
				chr(cls.block_size - len(s) % cls.block_size))

	@staticmethod
	def unpad(s):
		return s[:-ord(s[len(s) - 1:])]

	def create_share_link(self):
		cls = self.__class__
		pk_time_string = '{}__{}'.format(self.pk, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

		raw = self.pad(pk_time_string).encode(encoding='utf-8', errors='strict')
		iv = Random.new().read(cls.block_size)
		cipher = AES.new(cls.secret_key_link.encode(encoding='utf-8', errors='strict'), AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	@classmethod
	def check_share_link(cls, link):
		try:
			enc = base64.b64decode(link)
			iv = enc[:cls.block_size]
			cipher = AES.new(cls.secret_key_link.encode(encoding='utf-8', errors='strict'), AES.MODE_CBC, iv)
			bytes_string = cls.unpad(cipher.decrypt(enc[cls.block_size:]))
			pk_time_string = bytes_string.decode(encoding='utf-8')
			pk, time = pk_time_string.split('__')
		except ValueError:
			return None

		time_object = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
		delta_object = datetime.datetime.today() - datetime.timedelta(minutes=1)
		if (delta_object <= time_object):
			return pk

		return None

	def save(self, *args, **kwargs):
		self.login_password = self.encrypt_login_password()
		super().save(*args, **kwargs)

	def __str__(self):
		return self.site_name
