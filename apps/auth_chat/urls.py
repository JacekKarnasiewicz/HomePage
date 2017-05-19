from django.conf.urls import url

from .views import auth_chat


urlpatterns = [
	url(r'^$', auth_chat, name='auth_chat'),
]
