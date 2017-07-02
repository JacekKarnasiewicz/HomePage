from django.contrib.auth.forms import UserCreationForm
from django import forms


class CreateUser(UserCreationForm):
	username = forms.CharField(required=True, min_length=3, max_length=15)
