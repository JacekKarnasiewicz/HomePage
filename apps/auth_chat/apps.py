from django.apps import AppConfig


class AuthChatConfig(AppConfig):
	name = 'apps.auth_chat'

	def ready(self):
		import apps.auth_chat.signals
