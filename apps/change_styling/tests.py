from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase

from .views import change_styling


class ViewTest(TestCase):

	def test_change_styling_page_uses_correct_view(self):
		response = self.client.get(reverse('change_styling:change_styling'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, change_styling)

	def test_change_styling_page_render_correct_template(self):
		response = self.client.get(reverse('change_styling:change_styling'))

		self.assertTemplateUsed(response, 'change_styling/home.html')

	def test_change_styling_check_default_stylesheet_and_cookies(self):
		response = self.client.get(reverse('change_styling:change_styling'))

		self.assertFalse(response.wsgi_request.get_signed_cookie('styling', '', salt=settings.COOKIES_KEY))
		self.assertEqual(response.context['stylesheet_version'], 'css/base.css')

	def test_change_styling_POST_check_additional_stylesheets_and_cookies(self):
		cases = ('_blue', '_green', '_brink_pink')
		for case in cases:
			with self.subTest(case=case):
				response = self.client.post(reverse('change_styling:change_styling'), data={'styling': case}, follow=True)

				self.assertRedirects(response, reverse('change_styling:change_styling'), status_code=302, target_status_code=200)
				self.assertEqual(response.wsgi_request.get_signed_cookie('styling', '', salt=settings.COOKIES_KEY), case)
				self.assertEqual(response.context['stylesheet_version'], 'css/base{}.css'.format(case))

	def test_change_styling_POST_check_imaginary_stylesheet_and_cookies(self):
		response = self.client.post(reverse('change_styling:change_styling'), data={'styling': '_imaginary_color'}, follow=True)

		self.assertRedirects(response, reverse('change_styling:change_styling'), status_code=302, target_status_code=200)
		self.assertEqual(response.wsgi_request.get_signed_cookie('styling', '', salt=settings.COOKIES_KEY), '_imaginary_color')
		self.assertEqual(response.context['stylesheet_version'], 'css/base_imaginary_color.css')
