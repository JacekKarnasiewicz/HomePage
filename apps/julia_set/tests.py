from django.core.urlresolvers import reverse
from django.test import TestCase

from .forms import JuliaSetForm
from .views import julia_set


class FormTest(TestCase):
	
	def test_JuliaSetForm_empty_data(self):
		form = JuliaSetForm(data={})

		self.assertFalse(form.is_valid())
		self.assertIn('width', form.errors)

	def test_JuliaSetForm_default_data(self):
		form = JuliaSetForm(data={'width': '3000'})

		self.assertTrue(form.is_valid())

	def test_JuliaSetForm_valid_data(self):
		form = JuliaSetForm(data={
			'real_part': '-0.4',
			'imaginary_part': '0.27',
			'width': '2000',
			'max_iterations': '100',
			'sample': 'snowflake'})

		self.assertTrue(form.is_valid())

	def test_JuliaSetForm_invalid_data(self):
		form = JuliaSetForm(data={
			'real_part': '-2',
			'imaginary_part': '90',
			'width': '5000',
			'max_iterations': '0',
			'sample': 'unicorn'})

		self.assertFalse(form.is_valid())
		self.assertIn('real_part', form.errors)
		self.assertIn('imaginary_part', form.errors)
		self.assertIn('width', form.errors)
		self.assertIn('max_iterations', form.errors)
		self.assertIn('sample', form.errors)

	def test_JuliaSetForm_valid_sample(self):
		form = JuliaSetForm(data={'width': '3000', 'sample': 'stars'})

		self.assertTrue(form.is_valid())

	def test_JuliaSetForm_invalid_sample(self):
		form = JuliaSetForm(data={'width': '3000', 'sample': 'unicorn'})

		self.assertFalse(form.is_valid())
		self.assertIn('sample', form.errors)


class ViewTest(TestCase):

	def test_julia_set_page_usess_correct_view(self):
		response = self.client.get(reverse('julia_set:julia_set'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, julia_set)

	def test_julia_set_page_render_correct_tamplates(self):
		response = self.client.get(reverse('julia_set:julia_set'))

		self.assertTemplateUsed(response, 'julia_set/home.html')

	def test_julia_set_page_uses_correct_form(self):
		response = self.client.get(reverse('julia_set:julia_set'))

		self.assertIsInstance(response.context['form'], JuliaSetForm)

	def test_julia_set_page_default_valid_POST_headers(self):
		response = self.client.post(
			reverse('julia_set:julia_set'),
			data={
				'real_part': '',
				'imaginary_part': '',
				'width': '1000',
				'max_iterations': '',
				'sample': '',
				'submit': 'Generate Fractal'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('image/bmp', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_julia_set_page_valid_POST_headers(self):
		response = self.client.post(
			reverse('julia_set:julia_set'),
			data={
				'real_part': '0.123',
				'imaginary_part': '-0.721',
				'width': '1000',
				'max_iterations': '25',
				'sample': '',
				'submit': 'Generate Fractal'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('image/bmp', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_julia_set_page_valid_sample_POST_headers(self):
		response = self.client.post(
			reverse('julia_set:julia_set'),
			data={
				'real_part': '',
				'imaginary_part': '',
				'width': '1000',
				'max_iterations': '',
				'sample': 'stars',
				'submit': 'Generate Fractal'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('image/bmp', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_julia_set_page_invalid_POST(self):
		response = self.client.post(
			reverse('julia_set:julia_set'),
			data={
				'real_part': 'imaginary',
				'imaginary_part': '-44',
				'width': '-5000',
				'max_iterations': '500',
				'sample': 'unicorn',
				'submit': 'Generate Fractal'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('real_part', response.context['form'].errors)
		self.assertIn('imaginary_part', response.context['form'].errors)
		self.assertIn('width', response.context['form'].errors)
		self.assertIn('max_iterations', response.context['form'].errors)
		self.assertIn('sample', response.context['form'].errors)
