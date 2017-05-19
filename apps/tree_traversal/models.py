from django.db import models

from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey

class Catalog(MPTTModel):
	name = models.CharField(max_length=32, unique=True)
	parent = TreeForeignKey('self', blank=True, null=True, db_index=True, on_delete=models.CASCADE)

	def __str__(self):
		return self.name


class Item(models.Model):
	name = models.CharField(max_length=32, unique=True)
	link = models.URLField(max_length=255, blank=True, null=True)
	description = models.TextField()
	catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE)

	def __str__(self):
		return self.name
