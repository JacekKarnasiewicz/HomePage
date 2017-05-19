from django.conf.urls import url

from .views import codility


urlpatterns = [
	url(r'^$', codility, name='codility'),
]
