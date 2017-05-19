import numpy as np

from django import forms


class JuliaSetForm(forms.Form):
	real_part = forms.FloatField(
		required=False,
		widget=forms.NumberInput(attrs={'placeholder': 'Default value is randomize', 'step': 0.001}),
		min_value=-1,
		max_value=1)
	imaginary_part = forms.FloatField(
		required=False,
		widget=forms.NumberInput(attrs={'placeholder': 'Default value is randomize', 'step': 0.001}),
		min_value=-1,
		max_value=1)
	width = forms.ChoiceField(
		required=True,
		initial='1000',
		label='Choose picture width',
		choices=(('1000', '1000 (lowest quality and the fastest time to generate)'), ('2000', '2000'), ('3000', '3000 (highest quality and the slowest time to generate)')),
		widget=forms.RadioSelect)
	max_iterations = forms.IntegerField(
		required=False,
		widget=forms.NumberInput(attrs={'placeholder': 'Default value is 50'}),
		label='Maximum interations per pixel (less iteration means that color transition will be more distinct, but less accurate)',
		min_value=25,
		max_value=255)
	sample = forms.ChoiceField(
		required=False,
		label='Trouble finding nice fractal? Here are some predefined samples (names are make up, they represent my first thought about the pictures)',
		choices=(
			('cracks', 'cracks (real part is 0, imaginary is -0.8)'),
			('fern', 'fern (real part is -0.62772, imaginary is -0.42193)'),
			('snowflake', 'snowflake (real part is 0.0523, imaginary is 0.65)'),
			('snail', 'snail (real part is 0.285, imaginary is  0.01)'),
			('stars', 'stars (real part is 0.23686060081761018, imaginary is -0.6047908282494889)')),
		widget=forms.RadioSelect)

	def clean_real_part(self):
		real_part = self.cleaned_data.get('real_part')
		return real_part if real_part is not None else np.random.uniform(-1, 1, size=1)[0]

	def clean_imaginary_part(self):
		imaginary_part = self.cleaned_data.get('imaginary_part')
		return imaginary_part if imaginary_part is not None else np.random.uniform(-1, 1, size=1)[0]

	def clean_max_iterations(self):
		max_iterations = self.cleaned_data.get('max_iterations')
		return max_iterations if max_iterations is not None else 50

	def clean_width(self):
		width = self.cleaned_data.get('width')
		return int(width)
