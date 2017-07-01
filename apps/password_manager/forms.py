from django import forms

from .models import PasswordManager


class PasswordManagerForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.instance = kwargs.get('instance', None)
		super().__init__(*args, **kwargs)

		if self.instance and self.instance.pk:
			self.initial['login_password'] = self.instance.decrypt_login_password()

	def save(self, owner, *args, **kwargs):
		instance = super().save(commit=False)
		instance.owner = owner
		return instance.save()
	
	class Meta:
		model = PasswordManager
		fields = ('site_name', 'site_url', 'login_name', 'login_password')
		exclude = ('owner',)
