from django.conf import settings
from django.shortcuts import render, redirect

def change_styling(request):
	if request.method == 'POST':
		response = redirect('change_styling:change_styling')
		response.set_signed_cookie('styling', request.POST['styling'], salt=settings.COOKIES_KEY,
			max_age=None, expires=None, path='/', domain=None, secure=None, httponly=True)
		return response
	return render(request, 'change_styling/home.html')
