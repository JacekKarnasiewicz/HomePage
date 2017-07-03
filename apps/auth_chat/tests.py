from channels import Group
from channels.test import ChannelTestCase, HttpClient

from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.account.views import account

from .consumers import ws_post
from .models import LoggedInUser
from .views import auth_chat


User = auth.get_user_model()


class ChannelTest(ChannelTestCase):

	def test_consumers_functions(self):
		# TO DO
		client = HttpClient()
		user = User.objects.create_user(
			username='test1', email='test@test.com', password='123456')
		client.login(username='test1', password='123456')

		client2 = HttpClient()
		user = User.objects.create_user(
			username='test2', email='test@test.com', password='123456')
		client.login(username='test2', password='123456')

		client.send_and_consume('websocket.receive', text='hello')
		# Help needed !
		# How to test cosumers return values(from send() method) ?
		# client.receive() return None
		# client.get_next_message('websocket.receive') return None
		# client2.receive() return None

	def test_channels_Group(self):
		# Add a test channel to a test group
		Group("users").add("test-channel")
		# Send to the group
		Group("users").send({"value": 42})
		# Verify the message got into the destination channel
		result = self.get_next_message("test-channel", require=True)
		self.assertEqual(result['value'], 42)


class ModelTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.username = 'imaginary_name'
		cls.password = 'fake_password_123'
		cls.new_user = User.objects.create_user(username=cls.username, password=cls.password)
	
	def test_LoggedInUser_model_with_log_in(self):
		self.assertNotIn(self.username, LoggedInUser.objects.values_list('user__username', flat=True))

		self.client.login(username=self.username, password=self.password)

		self.assertIn(self.username, LoggedInUser.objects.values_list('user__username', flat=True))

	def test_LoggedInUser_model_with_log_out(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIn(self.username, LoggedInUser.objects.values_list('user__username', flat=True))

		self.client.logout()

		self.assertNotIn(self.username, LoggedInUser.objects.values_list('user__username', flat=True))

	def test_LoggedInUser_string_representation(self):
		self.client.login(username=self.username, password=self.password)
		self.assertEqual(str(LoggedInUser.objects.get(pk=self.new_user.pk)), self.username)


class ViewTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.username = 'imaginary_name'
		cls.password = 'imaginary_password_123'
		cls.new_user = User.objects.create_user(username=cls.username, password=cls.password)

	def test_auth_chat_page_uses_correct_view_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		response = self.client.get(reverse('auth_chat:auth_chat'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, auth_chat)

	def test_auth_chat_page_render_correct_template_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		response = self.client.get(reverse('auth_chat:auth_chat'))

		self.assertTemplateUsed(response, 'auth_chat/home.html')

	def test_auth_chat_page_uses_redirect_for_anonymous_user(self):
		response = self.client.get(reverse('auth_chat:auth_chat'))

		self.assertRedirects(response, '/account/?next=/auth_chat/', status_code=302, target_status_code=200)
