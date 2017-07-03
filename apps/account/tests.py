from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.test import TestCase

from .forms import CreateUser
from .views import account

User = auth.get_user_model()


class FormTest(TestCase):

	def test_CreateUser_form_for_empty_data(self):
		form = CreateUser(data={})

		self.assertFalse(form.is_valid())
		self.assertIn('username', form.errors)
		self.assertIn('password1', form.errors)
		self.assertIn('password2', form.errors)

	def test_CreateUser_form_for_valid_data(self):
		form = CreateUser(
			data={
				'username': 'imaginary_name',
				'password1': 'fake_password_123',
				'password2': 'fake_password_123',
			})

		self.assertTrue(form.is_valid())

	def test_CreateUser_form_for_invalid_data(self):
		form = CreateUser(
			data={
				'username': 'I',
				'password1': 'I',
				'password2': 'J',
			})

		self.assertFalse(form.is_valid())
		self.assertIn('username', form.errors)
		self.assertIn('password2', form.errors)


class ViewTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.username = 'imaginary_name'
		cls.password = 'imaginary_password_123'
		cls.new_user = User.objects.create_user(username=cls.username, password=cls.password)

	def test_account_page_uses_correct_view(self):
		response = self.client.get(reverse('account:account'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, account)

	def test_account_page_render_correct_template(self):
		response = self.client.get(reverse('account:account'))

		self.assertTemplateUsed(response, 'account/home.html')

	def test_account_page_uses_correct_forms(self):
		response = self.client.get(reverse('account:account'))

		self.assertIsInstance(response.context['create_user_form'], CreateUser)
		self.assertIsInstance(response.context['log_in_form'], AuthenticationForm)

	# def test_account_page_uses_redirect_for_logged_in_user(self):
	# 	self.client.login(username=self.username, password=self.password)
	# 	self.assertIsInstance(auth.get_user(self.client), User)

	# 	response = self.client.get(reverse('account:account'))

	# 	self.assertRedirects(response, '/', status_code=302, target_status_code=200)

	
	def test_account_page_valid_POST_for_create_user_form(self):
		response = self.client.post(
			reverse('account:account'),
			data={
				'username': 'bogus_name',
				'password1': 'password_123',
				'password2': 'password_123',
				'create_user_form': 'Create User',
			},
			follow=True)

		self.assertEqual(response.status_code, 200)

		user = auth.get_user(response.client)
		self.assertEqual(user.username, 'bogus_name')

	def test_account_page_invalid_POST_for_create_user_form(self):
		response = self.client.post(
			reverse('account:account'),
			data={
				'username': 'I',
				'password1': 'I',
				'password2': 'J',
				'create_user_form': 'Create User',
			})

		self.assertEqual(response.status_code, 200)
		self.assertIn('username', response.context['create_user_form'].errors)
		self.assertIn('password2', response.context['create_user_form'].errors)

	def test_account_page_valid_POST_for_log_in_form(self):
		response = self.client.post(
			reverse('account:account'),
			data={
				'username': self.username,
				'password': self.password,
				'log_in_form': 'Log in',
			},
			follow=True)

		self.assertEqual(response.status_code, 200)
		self.assertRedirects(response, '/', status_code=302, target_status_code=200)

		logged_in_user = auth.get_user(self.client)
		self.assertEqual(logged_in_user.username, self.new_user.username)

	def test_account_page_invalid_POST_for_log_in_form(self):
		response = self.client.post(
			reverse('account:account'),
			data={
				'username': 'fake_name',
				'password': 'fake_password',
				'log_in_form': 'Log in',
			},
			follow=True)

		self.assertEqual(response.status_code, 200)
		self.assertIn('__all__', response.context['log_in_form'].errors)

	def test_account_page_valid_POST_for_logging_out_user(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		response = self.client.get(reverse('account:account') + '?log_out', follow=True)

		self.assertEqual(response.status_code, 200)
		self.assertRedirects(response, '/', status_code=302, target_status_code=200)
		self.assertIsInstance(auth.get_user(self.client), auth.models.AnonymousUser)
