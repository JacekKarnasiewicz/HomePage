from django.apps import AppConfig


class SearchAppConfig(AppConfig):
	name = 'apps.search_app'

	def ready(self):
		import apps.search_app.signals
