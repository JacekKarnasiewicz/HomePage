from tempfile import NamedTemporaryFile

import pandas as pd

from django import forms
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.test import TestCase

from .context_processors import current_app
from .utilities import GenerateJuliaSet, PlotGraph

from apps.search_app.models import Applications


class ImaginaryForm(forms.Form):
	'Imaginary form for testing purpose'
	name = forms.CharField(max_length=10, required=True, help_text='Helpful text')
	description = forms.CharField(widget=forms.Textarea, required=True, help_text='Helpful text')
	option = forms.ChoiceField(
		required=True,
		help_text='Helpful text',
		choices=(('purple', 'purple'), ('classic', 'classic'), ('magenta', 'magenta')))
	boolean = forms.BooleanField(required=False, help_text='Helpful text')
	style = forms.ChoiceField(
		required=True,
		help_text='Helpful text',
		choices=(('purple', 'purple'), ('classic', 'classic'), ('magenta', 'magenta')),
		widget=forms.RadioSelect)
	picture = forms.FileField(required=True, max_length=256, help_text='Helpful text')

	def fake_method(self):
		'fake method for testing purpose'


class ContextProcessorTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.image = NamedTemporaryFile(suffix=".png").name
		cls.app = Applications.objects.create(name='App 1', description='...', image=cls.image,
			tags='python, django', url_source='http://example.com', url_name='search_app', visible=True)

	def test_current_app_function_valid(self):
		response = self.client.get(reverse('search_app:search_app'))
		self.assertEqual(current_app(response.wsgi_request).get('current_app', None), self.app)

	def test_current_app_function_invalid(self):
		response = self.client.get('/imaginary_url')
		self.assertEqual(current_app(response.wsgi_request).get('current_app', None), None)


class TemplatetagTest(TestCase):

	def test_form_field_tag_for_text_field(self):
		form = ImaginaryForm(prefix='imaginary_form')
		template = Template('{% load utility_tags %} {% form_field form.name %}')
		render_temp = template.render(Context({'form': form}))

		self.assertIn('class="form-group"', render_temp)
		self.assertIn('<label for="id_imaginary_form-name"', render_temp)
		self.assertIn('class="form-control"', render_temp)
		self.assertIn('type="text"', render_temp)
		self.assertIn('<span>*</span>', render_temp)
		self.assertNotIn('error', render_temp)
		self.assertIn('class="help-block"', render_temp)

	def test_form_field_tag_for_text_field_with_addon(self):
		form = ImaginaryForm(prefix='imaginary_form')
		template = Template('{% load utility_tags %} {% form_field form.name affix_addon="f(x) = " %}')
		render_temp = template.render(Context({'form': form}))

		self.assertIn('class="form-group"', render_temp)
		self.assertIn('<label for="id_imaginary_form-name"', render_temp)
		self.assertIn('class="input-group"', render_temp)
		self.assertIn('class="input-group-addon"', render_temp)
		self.assertIn('class="form-control"', render_temp)
		self.assertIn('type="text"', render_temp)
		self.assertIn('<span>*</span>', render_temp)
		self.assertNotIn('error', render_temp)
		self.assertIn('class="help-block"', render_temp)

	def test_form_field_tag_with_error(self):
		form = ImaginaryForm(prefix='imaginary_form', data={'imaginary_form-name': 'Incorrect long name'})
		template = Template('{% load utility_tags %} {% form_field form.name %}')
		render_temp = template.render(Context({'form': form}))

		self.assertIn('error_1', render_temp)
		self.assertIn('<strong>Ensure this value has at most 10 characters', render_temp)

	def test_form_field_tag_for_textarea(self):
		form = ImaginaryForm(prefix='imaginary_form')
		template = Template('{% load utility_tags %} {% form_field form.description %}')
		render_temp = template.render(Context({'form': form}))

		self.assertIn('class="form-group"', render_temp)
		self.assertIn('<label for="id_imaginary_form-description"', render_temp)
		self.assertIn('class="form-control"', render_temp)
		self.assertIn('type="text"', render_temp)
		self.assertIn('<span>*</span>', render_temp)
		self.assertIn('</textarea>', render_temp)
		self.assertNotIn('error', render_temp)
		self.assertIn('class="help-block"', render_temp)

	def test_form_field_tag_for_select_field(self):
		form = ImaginaryForm(prefix='imaginary_form')
		template = Template('{% load utility_tags %} {% form_field form.option %}')
		render_temp = template.render(Context({'form': form}))

		self.assertIn('class="form-group"', render_temp)
		self.assertIn('<label for="id_imaginary_form-option"', render_temp)
		self.assertIn('class="form-control"', render_temp)
		self.assertIn('<option value="magenta"', render_temp)
		self.assertNotIn('<option value="blue"', render_temp)
		self.assertIn('</select>', render_temp)
		self.assertIn('<span>*</span>', render_temp)
		self.assertNotIn('error', render_temp)
		self.assertIn('class="help-block"', render_temp)

	def test_form_field_tag_for_checkbox_field(self):
		form = ImaginaryForm(prefix='imaginary_form')
		template = Template('{% load utility_tags %} {% form_field form.boolean %}')
		render_temp = template.render(Context({'form': form}))

		self.assertIn('class="form-group"', render_temp)
		self.assertIn('<label for="id_imaginary_form-boolean"', render_temp)
		self.assertNotIn('class="form-control"', render_temp)
		self.assertIn('class="checkbox"', render_temp)
		self.assertNotIn('<span>*</span>', render_temp)
		self.assertNotIn('error', render_temp)
		self.assertIn('class="help-block"', render_temp)

	def test_form_field_tag_for_radio_field(self):
		form = ImaginaryForm(prefix='imaginary_form')
		template = Template('{% load utility_tags %} {% form_field form.style %}')
		render_temp = template.render(Context({'form': form}))

		self.assertIn('class="form-group"', render_temp)
		self.assertIn('<label for="id_imaginary_form-style"', render_temp)
		self.assertNotIn('class="form-control"', render_temp)
		self.assertIn('class="radio"', render_temp)
		self.assertIn('value="magenta"', render_temp)
		self.assertNotIn('value="blue"', render_temp)
		self.assertIn('<span>*</span>', render_temp)
		self.assertNotIn('error', render_temp)
		self.assertIn('class="help-block"', render_temp)

	def test_form_field_tag_for_file_field(self):
		form = ImaginaryForm(prefix='imaginary_form')
		template = Template('{% load utility_tags %} {% form_field form.picture %}')
		render_temp = template.render(Context({'form': form}))

		self.assertIn('class="form-group"', render_temp)
		self.assertIn('<label for="id_imaginary_form-picture"', render_temp)
		self.assertIn('class="input-group"', render_temp)
		self.assertIn('type="file"', render_temp)
		self.assertIn('class="form-control"', render_temp)
		self.assertIn('<span>*</span>', render_temp)
		self.assertNotIn('error', render_temp)
		self.assertIn('class="help-block"', render_temp)

	def test_attr_list_tag(self):
		template = Template('{% load utility_tags %} {% attr_list form %}')
		render_temp = template.render(Context({'form': ImaginaryForm}))

		self.assertIn('<p>is_valid</p>', render_temp)
		self.assertIn('<p>as_table</p>', render_temp)
		self.assertIn('<p>fake_method</p>', render_temp)


class UtilitiesTest(TestCase):

	def test_GenerateJuliaSet_valid_default_data(self):
		response = GenerateJuliaSet(0.4, -0.5).create_response()

		self.assertEqual(response.status_code, 200)
		self.assertEqual('image/bmp', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_GenerateJuliaSet_valid_data(self):
		response = GenerateJuliaSet(
			real_part=0.4,
			imaginary_part=-0.5,
			width=100,
			max_iterations=25).create_response()

		self.assertEqual(response.status_code, 200)
		self.assertEqual('image/bmp', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_GenerateJuliaSet_valid_sample(self):
		response = GenerateJuliaSet(
			sample='snail').create_response()

		self.assertEqual(response.status_code, 200)
		self.assertEqual('image/bmp', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_GenerateJuliaSet_invalid_sample(self):
		response = GenerateJuliaSet(
			sample='unicorn').create_response()

		self.assertEqual(response.status_code, 200)
		self.assertEqual('image/bmp', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_PlotGraph_valid_default_data(self):
		data_frame = pd.DataFrame(data=[(-1, 1), (0, 0), (1, 1)], columns=['X', 'Y'])
		response = PlotGraph(data_frame).create_response()

		self.assertEqual(response.status_code, 200)
		self.assertEqual('image/svg+xml', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_PlotGraph_valid_data(self):
		data_frame = pd.DataFrame(data=[(-1, 1), (0, 0), (1, 1)], columns=['X', 'Y'])
		response = PlotGraph(
			data_frame,
			title='Imaginary title',
			x_label='fake X',
			y_label='fake Y',
			extension='pdf',
			style='classic').create_response()

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/pdf', response['Content-Type'])
		self.assertIn('attachment;', response['Content-Disposition'])

	def test_PlotGraph_invalid_data(self):
		data_frame = pd.DataFrame(data=[(-1, 'k'), (0, 0), (1, 'm')], columns=['X', 'Y'])
		with self.assertRaises(ValueError):
			response = PlotGraph(data_frame).create_response()


class StaticFilesTest(TestCase):
	'Check if application contains required static files'

	def test_base_css(self):
		abs_path = finders.find('css/base.css', all=True)
		# self.assertTrue(staticfiles_storage.exists(abs_path))
		self.assertTrue(abs_path)

	def test_bootstrap_css(self):
		abs_path = finders.find('css/bootstrap.min.css', all=True)
		self.assertTrue(abs_path)

	def test_bootstrap_js(self):
		abs_path = finders.find('js/bootstrap.min.js', all=True)
		self.assertTrue(abs_path)

	def test_jumbotron_png(self):
		abs_path = finders.find('images/jumbotron.png', all=True)
		self.assertTrue(abs_path)
