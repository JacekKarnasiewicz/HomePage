from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404

from apps.search_app.models import Applications

def current_app(request):
	try:
		res = resolve(request.path)
		current_app = Applications.objects.get(url_name=res.app_name)
		return {
			'current_app': current_app,
		}
	# except Resolver404:
	except:
		return {}

def stylesheet_version(request):
	stylesheet_version = request.get_signed_cookie('styling', '', salt=settings.COOKIES_KEY)
	return {
		'stylesheet_version': 'css/base{}.css'.format(stylesheet_version),
	}
