from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import LoggedInUser

User = auth.get_user_model()


@login_required
def auth_chat(request):
	logged_in_users = User.objects.filter(id__in=LoggedInUser.objects.values_list('user', flat=True))

	return render(request, 'auth_chat/home.html', {'logged_in_users': logged_in_users})
