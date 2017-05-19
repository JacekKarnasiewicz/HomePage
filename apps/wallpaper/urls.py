from django.conf.urls import url

from .views import wallpaper


urlpatterns = [
	url(r'^$', wallpaper, name='wallpaper'),
]
