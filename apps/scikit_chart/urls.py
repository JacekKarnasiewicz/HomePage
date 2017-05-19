from django.conf.urls import url

from .views import scikit_chart, regression_line, k_nearest_neighborns


urlpatterns = [
	url(r'^$', scikit_chart, name='scikit_chart'),
	url(r'^regression_line/$', regression_line , name='regression_line'),
	url(r'^k_nearest_neighborns/$', k_nearest_neighborns , name='k_nearest_neighborns')
]
