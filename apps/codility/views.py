from django.shortcuts import render

from .models import CodilityTask

def codility(request):
	ctx = {'codility_task': CodilityTask.objects.all()}
	return render(request, 'codility/home.html', ctx)
