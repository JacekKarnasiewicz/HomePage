from django import forms


class WallpaperForm(forms.Form):
	search_phrase = forms.CharField(
		required=False,
		label='Search phrase e.g. Mclaren P1, Mountains Lake',
		max_length=64)
	random = forms.BooleanField(
		required=False,
		label='<span class="glyphicon glyphicon-alert" aria-hidden="true"></span> Random')

	def clean(self):
		cleaned_data = super(WallpaperForm, self).clean()
		if not cleaned_data.get('search_phrase') and not cleaned_data.get('random'):
			raise forms.ValidationError('Please provide search phrase or check random option.')
		return cleaned_data
