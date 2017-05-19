import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase

from .forms import PlotForm
from .views import mpl_graph


class FormTest(TestCase):

	def test_PlotForm_empty_data(self):
		form = PlotForm(data={})

		self.assertFalse(form.is_valid())
		self.assertFalse(hasattr(form, 'data_frame'))
		self.assertIn('extension', form.errors)
		self.assertIn('style', form.errors)

	def test_PlotForm_missing_source_data(self):
		form = PlotForm(data={
				'file': '',
				'custom_pattern': '',
				'min_value': '',
				'max_value': '',
				'step': '',
				'random': '',
				'extension': 'svg',
				'style': 'seaborn-dark-palette',
				'title': '',
				'x_label': '',
				'y_label': '',
				'submit': 'Generate Graph'})

		self.assertFalse(form.is_valid())
		self.assertFalse(hasattr(form, 'data_frame'))
		self.assertIn('__all__', form.errors)
		self.assertIn(
			'Please choose one plotting option, "file", "custom pattern" or "random" option.',
			form.errors['__all__'])

	def test_PlotForm_valid_file(self):
		f = SimpleUploadedFile("imaginary", b"x,y\n1,3\n2,5", content_type="image/png")

		form = PlotForm(
			data={
				'file': 'Imaginary File',
				'custom_pattern': '',
				'min_value': '',
				'max_value': '',
				'step': '',
				'random': '',
				'extension': 'svg',
				'style': 'seaborn-dark-palette',
				'title': '',
				'x_label': '',
				'y_label': '',
				'submit': 'Generate Graph'},
			files={'file': f})

		self.assertTrue(form.is_valid())
		self.assertTrue(hasattr(form, 'data_frame'))

	def test_PlotForm_valid_custom_pattern(self):
		form = PlotForm(
			data={
				'custom_pattern': 'x + 7',
				'extension': 'svg',
				'style': 'seaborn-dark-palette'})

		self.assertTrue(form.is_valid())
		self.assertTrue(hasattr(form, 'data_frame'))

	def test_PlotForm_invalid_custom_pattern(self):
		form = PlotForm(
			data={
				'custom_pattern': 'wx! + 4f7?',
				'extension': 'pdf',
				'style': 'seaborn-dark-palette'})

		self.assertFalse(form.is_valid())
		self.assertFalse(hasattr(form, 'data_frame'))
		self.assertIn('__all__', form.errors)
		self.assertIn(
			'Change a few things up and try submitting again.',
			form.errors['__all__'])

	def test_PlotForm_invalid_custom_pattern_values(self):
		form = PlotForm(data={
				'file': '',
				'custom_pattern': '',
				'min_value': '10',
				'max_value': '3',
				'step': '7',
				'random': '',
				'extension': 'svg',
				'style': 'seaborn-dark-palette',
				'title': '',
				'x_label': '',
				'y_label': '',
				'submit': 'Generate Graph'})

		self.assertFalse(form.is_valid())
		self.assertFalse(hasattr(form, 'data_frame'))
		self.assertIn('__all__', form.errors)
		self.assertIn('Please correct min, max or step value.', form.errors['__all__'])

	def test_PlotForm_field_validation_with_invalid_data(self):
		form = PlotForm(data={
			'file': '',
			'custom_pattern': '',
			'min_value': '-90000000',
			'max_value': '90000000',
			'step': '20',
			'random': '',
			'extension': '',
			'style': '',
			'title': '',
			'x_label': '',
			'y_label': '',
			'submit': 'Generate Graph'})

		self.assertFalse(form.is_valid())
		self.assertFalse(hasattr(form, 'data_frame'))
		self.assertIn('min_value', form.errors)
		self.assertIn('max_value', form.errors)
		self.assertIn('step', form.errors)
		self.assertIn('extension', form.errors)
		self.assertIn('style', form.errors)

	def test_PlotForm_clean_values(self):
		form = PlotForm(
			data={
				'custom_pattern': 'fabs(x*2 - 7)',
				'min_value': '',
				'max_value': '',
				'step': '',
				'extension': 'svg',
				'style': 'seaborn-dark-palette',
				'title': '',
				'x_label': '',
				'y_label': ''})

		self.assertTrue(form.is_valid())
		self.assertTrue(hasattr(form, 'data_frame'))
		self.assertTrue(-100, form.cleaned_data['min_value'])
		self.assertTrue(100, form.cleaned_data['max_value'])
		self.assertTrue(0.1, form.cleaned_data['step'])
		self.assertTrue('graph', form.cleaned_data['title'])
		self.assertTrue('X', form.cleaned_data['x_label'])
		self.assertTrue('Y', form.cleaned_data['y_label'])


class ViewTest(TestCase):

	def test_mpl_graph_page_uses_correct_view(self):
		response = self.client.get(reverse('mpl_graph:mpl_graph'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, mpl_graph)

	def test_mpl_graph_page_render_correct_template(self):
		response = self.client.get(reverse('mpl_graph:mpl_graph'))

		self.assertTemplateUsed(response, 'mpl_graph/home.html')

	def test_mpl_graph_page_uses_correct_form(self):
		response = self.client.get(reverse('mpl_graph:mpl_graph'))

		self.assertIsInstance(response.context['form'], PlotForm)

	def test_mpl_graph_form_valid_POST_headers(self):
		response = self.client.post(
			reverse('mpl_graph:mpl_graph'),
			data={
				'file': '',
				'custom_pattern': '-x**2',
				'min_value': '',
				'max_value': '',
				'step': '',
				'random': '',
				'extension': 'svg',
				'style': 'seaborn-dark-palette',
				'title': '',
				'x_label': '',
				'y_label': '',
				'submit': 'Generate Graph'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('image/svg+xml', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_mpl_graph_form_valid_POST_file(self):
		f = io.StringIO('X, Y\n1, 3\n7, 23')
		response = self.client.post(
			reverse('mpl_graph:mpl_graph'),
			data={
				'file': f,
				'custom_pattern': '',
				'min_value': '',
				'max_value': '',
				'step': '',
				'random': '',
				'extension': 'pdf',
				'style': 'classic',
				'title': '',
				'x_label': '',
				'y_label': '',
				'submit': 'Generate Graph'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('application/pdf', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_mpl_graph_form_valid_POST_random_data(self):
		response = self.client.post(
			reverse('mpl_graph:mpl_graph'),
			data={
				'file': '',
				'custom_pattern': '',
				'min_value': '',
				'max_value': '',
				'step': '',
				'random': True,
				'extension': 'png',
				'style': 'classic',
				'title': '',
				'x_label': '',
				'y_label': '',
				'submit': 'Generate Graph'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('image/png', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_mpl_graph_form_invalid_POST_no_data(self):
		response = self.client.post(
			reverse('mpl_graph:mpl_graph'),
			data={
				'file': '',
				'custom_pattern': '',
				'min_value': '',
				'max_value': '',
				'step': '',
				'random': '',
				'extension': 'svg',
				'style': 'seaborn-dark-palette',
				'title': '',
				'x_label': '',
				'y_label': '',
				'submit': 'Generate Graph'})

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].non_field_errors())

	def test_mpl_graph_form_invalid_POST_fields(self):
		response = self.client.post(
			reverse('mpl_graph:mpl_graph'),
			data={
				'file': '',
				'custom_pattern': 'x',
				'min_value': '-90000000',
				'max_value': '90000000',
				'step': '-100',
				'random': '',
				'extension': 'imaginary_extension',
				'style': 'imaginary_style',
				'title': '',
				'x_label': '',
				'y_label': '',
				'submit': 'Generate Graph'})

		self.assertIn('style', response.context['form'].errors)
		self.assertIn('extension', response.context['form'].errors)
		self.assertIn('step', response.context['form'].errors)
		self.assertIn('min_value', response.context['form'].errors)
		self.assertIn('max_value', response.context['form'].errors)
