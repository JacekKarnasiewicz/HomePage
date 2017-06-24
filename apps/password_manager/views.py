from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .forms import PasswordManagerForm
from .models import PasswordManager


def password_manager(request):
	ctx = {
		'password_manager': PasswordManager.objects.filter(owner=request.user.pk),
		'password_manager_form': PasswordManagerForm()
	}
	if request.method == 'POST' and request.is_ajax():
		print('VIEW IN ', request.user, request.POST, sep='\n')
		form = PasswordManagerForm(data=request.POST)
		if form.is_valid():
			print('Valid')
			form.save(owner=request.user)
			errors = False
		else:
			ctx['password_manager_form'] = form
			errors = True

		form_template = render_to_string('password_manager/form_modal.html', request=request, context=ctx)
		table_template = render_to_string('password_manager/table.html', request=request, context=ctx)
		return JsonResponse({'form_template': form_template, 'table_template': table_template, 'errors': errors})

	return render(request, 'password_manager/home.html', ctx)
