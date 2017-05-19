import os
from tempfile import NamedTemporaryFile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase

from .models import Applications, upload_path
from .views import search_app


class ModelTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.image = NamedTemporaryFile(suffix=".png").name
		cls.app = Applications.objects.create(name='App 1', description='...', image=cls.image,
			tags='python, django', url_source='http://example.com', url_name='one', visible=True)

	def test_delete_application(self):
		app = Applications.objects.create(name='App 2')
		self.assertIn(app, Applications.objects.all())
		app.delete()
		self.assertNotIn(app, Applications.objects.all())
	
	def test_unique_names(self):
		with self.assertRaisesRegexp(ValidationError, 'Applications with this Name already exists.'):
			Applications(name=self.app.name, description='...', image=self.image,
				tags='python, django', url_source='http://example.com', url_name='', visible=True
			).full_clean()

	def test_url_source_field(self):
		with self.assertRaisesRegexp(ValidationError, 'Enter a valid URL.'):
			Applications(name='App 2', description='...', image=self.image,
				tags='python, django', url_source='com', url_name='', visible=True).full_clean()

	def test_choice_for_url_name_field(self):
		with self.assertRaisesRegexp(ValidationError, "Value 'imaginary_url' is not a valid choice."):
			Applications(name='App 2', description='...', image=self.image,
				tags='python, django', url_source='http://example.com',
				url_name='imaginary_url', visible=True).full_clean()

	# test model methods
	def test_upload_path(self):
		image = SimpleUploadedFile("imaginary.png", b"", content_type="image/png")
		app = Applications(name='App 2', description='...', image=image,
			tags='python, django', url_source='http://example.com', url_name='two',
			visible=True)

		self.assertEqual(
			upload_path(app, image),
			'images/{0}/{1}'.format(app.url_name, app.image.name))

	def test_string_representation(self):
		self.assertEqual(str(self.app), self.app.name)

	# test signals
	def test_signal_delete_old_thumbnail(self):
		first_image = SimpleUploadedFile("first_image.png", b"", content_type="image/png")
		second_image = SimpleUploadedFile("second_image.png", b"", content_type="image/png")
		app = Applications.objects.create(name='App 2', description='...', image=first_image,
			tags='python, django', url_source='http://example.com', url_name='two',
			visible=True)

		self.assertIn(first_image.name, os.listdir(os.path.dirname(app.image.path)))

		app.image = second_image
		app.save(update_fields=['image'])

		self.assertNotIn(first_image.name, os.listdir(os.path.dirname(app.image.path)))
		self.assertIn(second_image.name, os.listdir(os.path.dirname(app.image.path)))

	def test_signal_delete_thumbnail_folder(self):
		image = SimpleUploadedFile("empty_image.png", b"", content_type="image/png")
		app = Applications.objects.create(name='App 2', description='...', image=image,
			tags='python, django', url_source='http://example.com', url_name='two',
			visible=True)

		image_path = app.image.path
		app_url_name = app.url_name
		self.assertIn(app_url_name, os.listdir(os.path.dirname(os.path.dirname(image_path))))

		app.delete()

		self.assertNotIn(app_url_name, os.listdir(os.path.dirname(os.path.dirname(image_path))))


class ViewTest(TestCase):

	def test_search_app_page_uses_correct_view(self):
		response = self.client.get(reverse('search_app:search_app'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, search_app)

	def test_search_app_page_render_correct_template(self):
		response = self.client.get(reverse('search_app:search_app'))

		self.assertTemplateUsed(response, 'search_app/home.html')
