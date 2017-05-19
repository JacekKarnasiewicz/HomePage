import base64
from concurrent import futures
import re

import requests

from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .forms import WallpaperForm


def wallpaper(request):
	form = WallpaperForm(data=request.POST or None)
	if request.method == 'POST' and form.is_valid():
		return StreamingHttpResponse(img_generator(request, form, form.cleaned_data.get('search_phrase'), form.cleaned_data.get('random')))
	return render(request, 'wallpaper/home.html', {'form': form})


def img_generator(request, form, search_phrase, random=None):
	yield render_to_string('wallpaper/head.html', request=request, context={'form': form})

	if random:
		response = requests.get('https://alpha.wallhaven.cc/random?page=1').text
	else:
		response = requests.get('https://alpha.wallhaven.cc/search?q={0}&purity=100&sorting=relevance&order=desc&page=1'.format(search_phrase)).text

	data = re.findall('data-src="https://alpha.wallhaven.cc/wallpapers/thumb/small/th-(.+?)" src=', response)

	if data:
		yield '<div class="row thumbnail-flex">'
		pool = futures.ThreadPoolExecutor(len(data))

		to_do_list = []
		for name in data:
			future = pool.submit(make_html, name)
			to_do_list.append(future)

		for future in futures.as_completed(to_do_list):
			yield future.result()
		yield '</div>'
	else:
		yield '<div class="row"><div class="text-center"><h4>Sorry, no wallpapers found</h4></div></div>'
	yield render_to_string('wallpaper/footer.html')


def make_html(name):
	extensions = {'png', 'jpg'}
	index, extension = name.split('.')
	response = requests.get('https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{}.{}'.format(index, extension))

	# It's weird but sometimes thumbnails have different extensions in compare to regular picture on wallhaven portal
	if response.status_code != 200:
		extension = extensions.difference(set(extension)).pop()
		response = requests.get('https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{}.{}'.format(index, extension))
		if response.status_code != 200:
			return ''

	content = response.content
	data = base64.b64encode(content)
	data = data.decode('ascii')

	return """<div class="col-xs-12 col-sm-6 col-md-4 col-lg-4">
		<div class="thumbnail">
			<img data-src="" alt="100%x200" style="height: 200px; width: 100%; display: block;" src="data:image/{0};base64,{1}" data-holder-rendered="true">
		</div>
	</div>""".format(extension, data)










# ALTERNATIVE VERSION(JsonResponse)
# from django.http import JsonResponse 

# def wallpaper(request):
# 	form = WallpaperForm(data=request.POST or None)
# 	if request.method == 'POST' and form.is_valid() and request.is_ajax():
# 		template = convert_images(form.cleaned_data.get('search_phrase'), form.cleaned_data.get('random'))
# 		return JsonResponse({'template': template})
# 	return render(request, 'wallpaper/home.html', {'form': form})


# def convert_images(search_phrase, random=None):
# 	if random:
# 		response = requests.get('https://alpha.wallhaven.cc/random?page=2').text
# 	else:
# 		response = requests.get('https://alpha.wallhaven.cc/search?q={0}&purity=100&resolutions=1920x1080&sorting=relevance&order=desc&page=1'.format(search_phrase)).text

# 	data = re.findall('data-src="https://alpha.wallhaven.cc/wallpapers/thumb/small/th-(.+?)" src=', response)

# 	with futures.ThreadPoolExecutor(len(data)) as executor:
# 		# create generator
# 		result = executor.map(make_base64_image, data)

# 	result = filter(bool, result)
# 	return render_to_string('wallpaper/search_results.html', context={'result': result})


# def make_base64_image(index):
# 	extensions = {'png', 'jpg'}
# 	index, extension = index.split('.')
# 	response = requests.get('https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{}.{}'.format(index, extension))

# 	# It's weird but sometimes thumbnails have different extensions in compare to regular picture on wallhaven portal
# 	if response.status_code != 200:
# 		extension = extensions.difference(set(extension)).pop()
# 		response = requests.get('https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{}.{}'.format(index, extension))
# 		if response.status_code != 200:
# 			return None

# 	content = response.content
# 	data = base64.b64encode(content)
# 	data = data.decode('ascii')
# 	return extension, data


# ADD TO 'home.html'

# <div class="row">
# 	<div class="col-xs-12 col-sm-12 col-md-12 col-lg-12">
# 		<div id="search_result"></div>
# 	</div>
# </div>

# <script type="text/javascript">
# 	$(document).ready(function() {
# 		// ajax
# 		$('form').submit(function(e) {
# 			e.preventDefault();

# 			let form_data = new FormData(this);
			
# 			$.ajax({
# 				url: {% url 'wallpaper:wallpaper' %},
# 				type: 'POST',
# 				data: form_data,
# 				processData: false,
# 				contentType: false,
# 				cache: false,
# 				beforeSend: function () {
# 					$("body").css("cursor", "wait");
# 				},
# 				success: function(data) {
# 					$('#search_result').html(data.template);
# 				},
# 				error: function() {
# 					console.log('AJAX ERROR');
# 				},
# 				complete: function() {
# 					$("body").css("cursor", "default");
# 				}
# 			});
# 		});
# 	})
# </script>


# CREATE 'search_results.html'
# <div class="row thumbnail-flex">
# 	{% for extension, data_img in result %}
# 	<div class="col-sm-6 col-md-4 col-lg-4 app_thumbnail">
# 		<div class="thumbnail">
# 			<img data-src="" alt="100%x200" style="height: 200px; width: 100%; display: block;" src="data:image/{{ extension }};base64,{{ data_img }}" data-holder-rendered="true">
# 		</div>
# 	</div>
# 	{% empty %}
# 	<div class="text-center">
# 		<h3>Sorry, no image available</h3>
# 	</div>
# 	{% endfor %}
# </div>
