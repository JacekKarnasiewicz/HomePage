from django.conf.urls import url

from .views import julia_set


urlpatterns = [
	url(r'^$', julia_set, name='julia_set')
]
