from unittest.mock import patch

from django.test import TestCase
from django.core.urlresolvers import reverse

from .forms import WallpaperForm
from .views import make_html, wallpaper


class FormTest(TestCase):

	def test_WallpaperForm_search_phrase_max_length(self):
		form = WallpaperForm(data={'search_phrase': 65*'a'})

		self.assertFalse(form.is_valid())
		self.assertIn('search_phrase', form.errors)

	def test_WallpaperForm_missing_data(self):
		form = WallpaperForm(data={})

		self.assertFalse(form.is_valid())
		self.assertIn('__all__', form.errors)


class ViewTest(TestCase):

	def test_wallpaper_page_usess_correct_view(self):
		response = self.client.get(reverse('wallpaper:wallpaper'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, wallpaper)

	def test_wallpaper_page_render_correct_tamplates(self):
		response = self.client.get(reverse('wallpaper:wallpaper'))

		self.assertTemplateUsed(response, 'wallpaper/home.html')

	def test_wallpaper_page_uses_correct_form(self):
		response = self.client.get(reverse('wallpaper:wallpaper'))

		self.assertIsInstance(response.context['form'], WallpaperForm)

	def test_wallpaper_page_invalid_POST_empty_data(self):
		response = self.client.post(reverse('wallpaper:wallpaper'), data={'search_phrase': '', 'random': ''})

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].non_field_errors())

	def test_wallpaper_page_valid_POST_search_phrase_option(self):
		response = self.client.post(reverse('wallpaper:wallpaper'), data={'search_phrase': 'imaginary', 'random': ''})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<div class="thumbnail">')


	def test_wallpaper_page_invalid_POST_search_phrase_option(self):
		response = self.client.post(reverse('wallpaper:wallpaper'), data={'search_phrase': 'iiiiiiiIIIIIII', 'random': ''})

		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, '<div class="thumbnail">')

	def test_wallpaper_page_valid_POST_random_option(self):
		response = self.client.post(reverse('wallpaper:wallpaper'), data={'search_phrase': '', 'random': True})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<div class="thumbnail">')


class FunctionTest(TestCase):

	def test_make_html_function(self):
		with patch('requests.get') as response:
			response.status_code.return_value = 404
			result = make_html('fake_name.png')

		self.assertEqual(result, '')
