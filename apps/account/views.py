from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import resolve
from django.shortcuts import redirect, render

from .forms import CreateUser

User = auth.get_user_model()


def account(request):
	create_user_form = CreateUser()
	log_in_form = AuthenticationForm()
	redirect_to = request.GET.get('next', '/')

	if request.method == 'POST' and 'create_user_form' in request.POST:
		create_user_form = CreateUser(data=request.POST or None)
		if create_user_form.is_valid():
			create_user_form.save()
			user = auth.authenticate(username=create_user_form.cleaned_data['username'],
								 	 password=create_user_form.cleaned_data['password1'])
			auth.login(request, user)
			return redirect(redirect_to)

	if request.method == 'POST' and 'log_in_form' in request.POST:
		log_in_form = AuthenticationForm(data=request.POST or None)
		if log_in_form.is_valid():
			auth.login(request, log_in_form.get_user())
			return redirect(redirect_to)

	if request.method == 'GET' and 'log_out' in request.GET:
		auth.logout(request)
		return redirect('search_app:search_app')

	return render(
		request,
		'account/home.html',
		{'create_user_form': create_user_form,
		 'log_in_form': log_in_form})
