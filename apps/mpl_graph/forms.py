import math

import numpy as np
import pandas as pd

from django import forms


class PlotForm(forms.Form):
	file = forms.FileField(
		required=False,
		max_length=256,
		label='Plot from csv file',
		help_text='Select one file with two or more columns separated by commas')
	custom_pattern = forms.CharField(
		required=False,
		max_length=64,
		label='Plot from custom pattern e.g. x**2 - 6*x + 5 (functions from math module are available e.g. sqrt, sin, floor)',
		help_text='Have fun and good luck ...and if you manage to destroy my app, please tell me how did you do that :), and I will try to fix that')
	min_value = forms.FloatField(
		required=False,
		label='Min value of x',
		widget=forms.NumberInput(attrs={'placeholder': 'Default value is -100'}),
		min_value=-1000000,
		max_value=1000000)
	max_value = forms.FloatField(
		required=False,
		label='Max value of x',
		widget=forms.NumberInput(attrs={'placeholder': 'Default value is 100'}),
		min_value=-1000000,
		max_value=1000000)
	step = forms.FloatField(
		required=False,
		widget=forms.NumberInput(attrs={'placeholder': 'Default value is 0.1', 'step': 0.001}),
		min_value=0.001,
		max_value=10)
	random = forms.BooleanField(
		required=False,
		label='Plot from random data')
	extension = forms.ChoiceField(
		required=True,
		initial='svg',
		label='Choose file format of the graph (extension)',
		choices=(('pdf', 'pdf'), ('svg', 'svg'), ('png', 'png')),
		widget=forms.RadioSelect)
	style = forms.ChoiceField(
		required=True,
		initial='seaborn-dark-palette',
		label='Choose matplotlib(pyplot) style',
		choices=(('bmh', 'bmh'), ('classic', 'classic'), ('seaborn-dark-palette', 'seaborn-dark-palette')),
		widget=forms.RadioSelect)
	title = forms.CharField(
		required=False,
		max_length=32,
		label='Title of the graph',
		widget=forms.TextInput(attrs={'placeholder': 'Default title is "graph"'}))
	x_label = forms.CharField(
		required=False,
		max_length=32,
		label="Label for x's",
		widget=forms.TextInput(attrs={'placeholder': 'Default label is "X"'}))
	y_label = forms.CharField(
		required=False,
		max_length=32,
		label="Label for y's",
		widget=forms.TextInput(attrs={'placeholder': 'Default label is "Y"'}))

	def clean_title(self):
		title = self.cleaned_data['title']
		return title if title else 'graph'

	def clean_min_value(self):
		min_value = self.cleaned_data.get('min_value')
		return min_value if min_value is not None else -100

	def clean_max_value(self):
		max_value = self.cleaned_data.get('max_value')
		return max_value if max_value is not None else 100

	def clean_step(self):
		step = self.cleaned_data.get('step')
		return step if step else 0.1

	def clean_x_label(self):
		x_label = self.cleaned_data.get('x_label')
		return x_label if x_label else 'X'

	def clean_y_label(self):
		y_label = self.cleaned_data.get('y_label')
		return y_label if y_label else 'Y'

	def clean(self):
		""" Creating pandas DataFrame from random, custom_pattern or file option """

		cleaned_data = super(PlotForm, self).clean()
		# ?! In case when field validators detect error corresponding clean_field is omitted
		if self.errors:
			return cleaned_data

		random = cleaned_data.get('random')
		custom_pattern = cleaned_data.get('custom_pattern')
		file = cleaned_data.get('file')
		min_value = cleaned_data.get('min_value')
		max_value = cleaned_data.get('max_value')
		step = cleaned_data.get('step')

		if min_value >= max_value or min_value + step > max_value:
			raise forms.ValidationError('Please correct min, max or step value.')

		if not random and not custom_pattern and not file:
			raise forms.ValidationError('Please choose one plotting option, "file", "custom pattern" or "random" option.')

		eval_globals = {"__builtins__": None}
		eval_locals = {func: getattr(math, func) for func in dir(math) if not func.startswith('__')}
		try:
			if random:
				x_range = np.arange(np.random.randint(-100, 0), np.random.randint(0, 100), np.random.choice((0.1, 0.01)))
				sample_functions = np.random.choice((
					'0.5*x - 4',
					'-x**2 + 7*x + 12',
					'5*sin(0.5*x)',
					'floor(x)',
					'tanh(x)',
					'0.5*exp(x) - 7',
					'cosh(x)',
					'-sqrt(sqrt(fabs(x)))'))
				y = (eval(sample_functions, eval_globals, eval_locals) for x in x_range if not eval_locals.update({'x': x}))
				self.data_frame = pd.DataFrame(data=list(zip(x_range, y)), columns=['X', sample_functions])
			elif custom_pattern:
				x_range = np.arange(min_value, max_value + self.fields['step'].min_value, step)
				y = (float(eval(custom_pattern, eval_globals, eval_locals)) for x in x_range if not eval_locals.update({'x': x}))
				self.data_frame = pd.DataFrame(data=list(zip(x_range, y)), columns=['X', custom_pattern])
			elif file:
				self.data_frame = pd.read_csv(file)
		except:
			raise forms.ValidationError('Change a few things up and try submitting again.')

		return cleaned_data
