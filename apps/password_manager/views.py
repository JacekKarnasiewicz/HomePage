from json import loads

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from .forms import PasswordManagerForm
from .models import PasswordManager
from .utilities import CheckPassword


@login_required
def password_manager(request):
	ctx = {
		'password_manager': PasswordManager.objects.filter(owner=request.user.pk),
	}
	return render(request, 'password_manager/home.html', ctx)


@login_required
def create_password(request):
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


@login_required
def edit_password(request, password_pk):
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


@login_required
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


@login_required
def check_password(request):
	if request.method == 'POST' and request.is_ajax():
		data = loads(request.body.decode('utf-8'))
		password_object = CheckPassword(data['password'])

		bits_of_entropy = password_object.get_bits_of_entropy()
		progress_bar_percent = 100 if bits_of_entropy > 100 else bits_of_entropy
		annotations = password_object.get_annotations()
		password_strength = password_object.get_password_strength().upper()

		ctx = {
			'bits_of_entropy': bits_of_entropy,
			'progress_bar_percent': progress_bar_percent,
			'annotations': annotations,
			'password_strength': password_strength
		}

		password_template = render_to_string('password_manager/password_information.html', request=request, context=ctx)
		return JsonResponse({'password_template': password_template})

	raise Http404('Resource Not Found')


@login_required
def generate_link(request, obj_pk):
	obj = get_object_or_404(PasswordManager, pk=obj_pk)

	if request.user != obj.owner:
		raise Http404('Resource Not Found')

	host = request.get_host()
	link = reverse('password_manager:access_link', kwargs={'link': obj.create_share_link()})
	link_template = render_to_string(
		'password_manager/link_modal.html',
		request=request,
		context={'link': host + link})
	return JsonResponse({'link_template': link_template})


@login_required
def access_link(request, link):
	ctx = {}
	obj_pk = PasswordManager.check_share_link(link)
	if obj_pk:
		obj = get_object_or_404(PasswordManager, pk=obj_pk)
		ctx['password'] = obj.decrypt_login_password()
		ctx['message'] = '{} share with you password for {} site:'.format(obj.owner, obj.site_name)
	else:
		ctx['message'] = "Link has expired or doesn't exists"
	return render(request, 'password_manager/access_link.html', ctx)
