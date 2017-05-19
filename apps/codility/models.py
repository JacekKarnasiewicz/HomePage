from django.db import models


class CodilityTask(models.Model):
	title = models.CharField(max_length=128, unique=True)
	annotation = models.CharField(max_length=256)
	code = models.TextField()
	link = models.URLField(max_length=128)

	def __str__(self):
		return self.title
