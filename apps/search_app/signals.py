import os
import shutil

from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from .models import Applications

@receiver(pre_save, sender=Applications)
def delete_old_thumbnail(sender, instance, *args, **kwargs):
	if instance.pk is not None:
		image = Applications.objects.get(pk=instance.pk).image
		if image and (image.name != instance.image.name):
			image.delete(save=False)


@receiver(post_delete, sender=Applications)
def delete_thumbnail_folder(sender, instance, *args, **kwargs):
	if instance.image:
		shutil.rmtree(os.path.dirname(instance.image.path), ignore_errors=True)
