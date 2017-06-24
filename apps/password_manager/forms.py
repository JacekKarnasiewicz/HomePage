from django import forms

from .models import PasswordManager


class PasswordManagerForm(forms.ModelForm):

	# def __init__(self, *args, **kwargs):
	# 	self.owner = kwargs.pop('owner', None)
	# 	super().__init__(*args, **kwargs)

	def save(self, owner, *args, **kwargs):
		# self.cleaned_data['owner'] = owner
		instance = super().save(commit=False)
		instance.owner = owner
		return instance.save()
	# def clean_owner(self):
	# 	print('clean owner')
	# 	owner = self.cleaned_data['owner']
	# 	print(owner)
	# 	return self.owner
	# def clean(self):
	# 	print('CLEAN')
	# 	cleaned_data = super().clean()
	# 	cleaned_data['owner'] = self.owner.pk
	# 	return cleaned_data

	
	class Meta:
		model = PasswordManager
		fields = ('site_name', 'site_url', 'login_name', 'login_password')
		exclude = ('owner',)
