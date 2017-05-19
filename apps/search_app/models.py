import os

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse


def avaiable_apps():
	dir_names = next(os.walk(os.path.join(settings.BASE_DIR, 'apps')))[1]
	choices = [(item, item) for item in dir_names if not item.startswith('__')]
	return choices

def upload_path(instance, filename):
	return 'images/{0}/{1}'.format(instance.url_name, filename)


class Applications(models.Model):
	name = models.CharField(
		max_length=64,
		unique=True)
	description = models.TextField()
	tags = models.CharField(max_length=128)
	image = models.ImageField(upload_to=upload_path)
	url_source = models.URLField(max_length=128)
	url_name = models.CharField(
		unique = True,
		max_length=128,
		choices=avaiable_apps())
	visible = models.BooleanField(default=True)

	class Meta:
		ordering = ('?',)
		verbose_name = 'Applications'
		verbose_name_plural = 'Applications'

	def get_absolute_url(self):
		return reverse('{0}:{0}'.format(self.url_name))

	def __str__(self):
		return self.name
