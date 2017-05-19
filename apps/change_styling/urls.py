from django.conf.urls import url

from .views import change_styling


urlpatterns = [
	url(r'^$', change_styling, name='change_styling'),
]
