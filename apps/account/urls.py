from django.conf.urls import url

from .views import account


urlpatterns = [
	url(r'^$', account, name='account'),
]
