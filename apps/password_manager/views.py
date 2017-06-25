from json import loads

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from .forms import PasswordManagerForm
from .models import PasswordManager


def password_manager(request):
	ctx = {
		'password_manager': PasswordManager.objects.filter(owner=request.user.pk),
	}
	return render(request, 'password_manager/home.html', ctx)


def create_password(request):
	print('CREATE PASSWORD')
	ctx = {
		'password_manager': PasswordManager.objects.filter(owner=request.user.pk),
		'password_manager_form': PasswordManagerForm()
	}
	if request.method == 'POST' and request.is_ajax():
		form = PasswordManagerForm(data=request.POST)
		if form.is_valid():
			form.save(owner=request.user)
			errors = False
		else:
			ctx['password_manager_form'] = form
			errors = True

		form_template = render_to_string('password_manager/form_modal.html', request=request, context=ctx)
		table_template = render_to_string('password_manager/table.html', request=request, context=ctx)
		return JsonResponse({'form_template': form_template, 'table_template': table_template, 'errors': errors})

	form_template = render_to_string('password_manager/form_modal.html', request=request, context=ctx)
	return JsonResponse({'form_template': form_template})



def edit_password(request, password_pk):
	print('EDIT PASSWORD')
	obj = get_object_or_404(PasswordManager, pk=password_pk)

	ctx = {
		'password_manager': PasswordManager.objects.filter(owner=request.user.pk),
		'password_manager_form': PasswordManagerForm(instance=obj),
		'object_pk': obj.pk
	}

	if request.method == 'POST' and request.is_ajax():
		form = PasswordManagerForm(data=request.POST, instance=obj)
		if form.is_valid():
			if request.user == obj.owner:
				form.save(owner=request.user)
				errors = False
			else:
				raise Http404('Not Allowed')
		else:
			ctx['password_manager_form'] = form
			errors = True

		form_template = render_to_string('password_manager/form_modal.html', request=request, context=ctx)
		table_template = render_to_string('password_manager/table.html', request=request, context=ctx)
		return JsonResponse({'form_template': form_template, 'table_template': table_template, 'errors': errors})

	form_template = render_to_string('password_manager/form_modal.html', request=request, context=ctx)
	return JsonResponse({'form_template': form_template})


def delete_password(request):
	if request.method == 'POST' and request.is_ajax():
		data = loads(request.body.decode('utf-8'))
		obj = get_object_or_404(PasswordManager, pk=data['id'])
		if request.user == obj.owner:
			obj.delete()

			ctx = {'password_manager': PasswordManager.objects.filter(owner=request.user.pk)}
			table_template = render_to_string('password_manager/table.html', request=request, context=ctx)
			return JsonResponse({'table_template': table_template})
		else:
			raise Http404('Not Allowed')

	raise Http404('Resource Not Found')
