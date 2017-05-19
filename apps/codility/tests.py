from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import CodilityTask
from .views import codility


class ModelTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.codility_task = CodilityTask.objects.create(
			title='Lesson 7', annotation='No annotations', code='...', link='http://example.com')

	def test_delete_codility_task(self):
		task = CodilityTask.objects.create(
			title='Lesson 1', annotation='No annotations', code='...', link='http://example.com')

		self.assertIn(task, CodilityTask.objects.all())
		task.delete()
		self.assertNotIn(task, CodilityTask.objects.all())

	def test_unique_titles(self):
		with self.assertRaisesRegexp(ValidationError, 'Codility task with this Title already exists.'):
			CodilityTask(title='Lesson 7', annotation='No annotations', code='...', link='http://example.com').full_clean()

	def test_link_field(self):
		with self.assertRaisesRegexp(ValidationError, 'Enter a valid URL.'):
			CodilityTask(title='Lesson 3', annotation='No annotations', code='...', link='.com').full_clean()		
	
	def test_string_representation(self):
		self.assertEqual(str(self.codility_task), self.codility_task.title)


class ViewTest(TestCase):
	
	def test_codility_page_uses_correct_view(self):
		response = self.client.get(reverse('codility:codility'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, codility)

	def test_codility_page_render_correct_template(self):
		response = self.client.get(reverse('codility:codility'))

		self.assertTemplateUsed(response, 'codility/home.html')
