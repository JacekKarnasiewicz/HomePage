from django.conf.urls import url

from .views import (
	PasswordManagerListAPIView,
	PasswordManagerRetrieveAPIView,
	PasswordManagerCreateAPIView,
	PasswordManagerUpdateAPIView,
	PasswordManagerDestroyAPIView,
	)

urlpatterns = [
	url(r'^$', PasswordManagerListAPIView.as_view(), name='list'),
	url(r'^retrieve/(?P<site_name>[\w]+)/$', PasswordManagerRetrieveAPIView.as_view(), name='retrieve'),
	url(r'^create/$', PasswordManagerCreateAPIView.as_view(), name='create'),	
	url(r'^update/(?P<site_name>[\w]+)/$', PasswordManagerUpdateAPIView.as_view(), name='update'),
	url(r'^destroy/(?P<site_name>[\w]+)/$', PasswordManagerDestroyAPIView.as_view(), name='destroy'),
]
