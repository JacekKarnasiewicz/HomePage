from django.conf.urls import url

from .views import search_app


urlpatterns = [
	url(r'^$', search_app, name='search_app'),
]
