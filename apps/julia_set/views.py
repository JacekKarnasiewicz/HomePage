from django.shortcuts import render

from HomePage.utilities import GenerateJuliaSet

from .forms import JuliaSetForm


def julia_set(request):
	form = JuliaSetForm(data=request.POST or None)
	if request.method == 'POST' and form.is_valid():
		response = GenerateJuliaSet(
			real_part=form.cleaned_data['real_part'],
			imaginary_part=form.cleaned_data['imaginary_part'],
			width=form.cleaned_data['width'],
			max_iterations=form.cleaned_data['max_iterations'],
			sample=form.cleaned_data['sample']).create_response()
		return response
	return render(request, 'julia_set/home.html', {'form': form})
