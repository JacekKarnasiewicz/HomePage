from django.shortcuts import render

from HomePage.utilities import PlotGraph

from .forms import PlotForm


def mpl_graph(request):
	ctx = {'form': PlotForm(data=request.POST or None, files=request.FILES or None)}
	if request.method == 'POST':
		if ctx['form'].is_valid():
			response = PlotGraph(
				data_frame=ctx['form'].data_frame,
				title=ctx['form'].cleaned_data['title'],
				x_label=ctx['form'].cleaned_data['x_label'],
				y_label=ctx['form'].cleaned_data['y_label'],
				extension=ctx['form'].cleaned_data['extension'],
				style=ctx['form'].cleaned_data['style']).create_response()
			return response

	return render(request, 'mpl_graph/home.html', ctx)
