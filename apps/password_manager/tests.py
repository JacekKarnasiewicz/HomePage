from json import dumps, loads

from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase

from .forms import PasswordManagerForm
from .models import PasswordManager
from .utilities import CheckPassword
from .views import password_manager

User = auth.get_user_model()


class UtilitiesTest(TestCase):

	def test_CheckPassword_empty_password(self):
		pass_obj = CheckPassword('')

		self.assertEqual(pass_obj.get_bits_of_entropy(), 0)
		self.assertEqual(len(pass_obj.get_annotations()), 1)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[0])
	
	def test_CheckPassword_short_password(self):
		pass_obj = CheckPassword('abcd')

		self.assertEqual(pass_obj.get_bits_of_entropy(), 0)
		self.assertEqual(len(pass_obj.get_annotations()), 1)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[0])

	def test_CheckPassword_only_lower_case_characters(self):
		pass_obj = CheckPassword('abcdefghij')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 47, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 3)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[1])

	def test_CheckPassword_only_upper_case_characters(self):
		pass_obj = CheckPassword('ABCDEFGHIJ')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 47, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 3)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[1])

	def test_CheckPassword_only_number_characters(self):
		pass_obj = CheckPassword('0133557799')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 33.2, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 3)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[0])

	def test_CheckPassword_only_special_characters(self):
		pass_obj = CheckPassword('!@#$%^&*()')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 50, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 3)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[1])

	def test_CheckPassword_lower_and_upper_case_characters(self):
		pass_obj = CheckPassword('abcdeFGHIJ')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 57, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 2)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[1])

	def test_CheckPassword_lower_and_upper_case_characters_with_numbers(self):
		pass_obj = CheckPassword('abcdEFGH01')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 59.5, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 1)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[1])

	def test_CheckPassword_lower_and_upper_case_characters_with_numbers_and_special_characters(self):
		pass_obj = CheckPassword('abcDEF01!@')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 65.5, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 0)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[2])

	def test_CheckPassword_long_password_lower_and_upper_case_characters_with_numbers_and_special_characters(self):
		pass_obj = CheckPassword('abcDEF01!@qieRTY34#$')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 131.09, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 0)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[4])

	def test_CheckPassword_password_mutations(self):
		pass_obj = CheckPassword('abcP@s$w0rD')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 72.1, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 1)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[2])

	def test_CheckPassword_common_substrings(self):
		pass_obj = CheckPassword('#$R9tjzqAz?.')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 78.65, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 1)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[2])


class ModelTest(TestCase):
	
	@classmethod
	def setUpTestData(cls):
		cls.username = 'bogus_name'
		cls.password = 'bogus_password_123'
		cls.new_user = User.objects.create_user(username=cls.username, password=cls.password)

		cls.login_password = 'imaginary_password'
		cls.pass_obj = PasswordManager.objects.create(owner=cls.new_user, site_name='imaginary_name',
			site_url='http://example.com', login_name='imaginary_login', login_password=cls.login_password)

	def test_unique_site_name(self):
		with self.assertRaisesRegexp(ValidationError, 'Password manager with this Site name already exists.'):
			PasswordManager(owner=self.new_user, site_name='imaginary_name', site_url='http://example.com',
			login_name='fake_login', login_password='fake_password').full_clean()

	def test_site_url(self):
		with self.assertRaisesRegexp(ValidationError, 'Enter a valid URL.'):
			PasswordManager(owner=self.new_user, site_name='fake_name', site_url='example',
				login_name='fake_login', login_password='fake_password').full_clean()

	def test_decrypt_login_password_method(self):
		self.assertEqual(self.pass_obj.decrypt_login_password(), self.login_password)

	def test_save_method(self):
		login_password = 'fake_password'
		new_pass_obj = PasswordManager(owner=self.new_user, site_name='fake_name',
			site_url='http://example.com', login_name='fake_login', login_password=login_password)

		new_pass_obj.save()

		self.assertNotEqual(new_pass_obj.login_password, login_password)

	def test_string_representation(self):
		self.assertEqual(str(self.pass_obj), self.pass_obj.site_name)


class FormTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.username = 'bogus_name'
		cls.password = 'bogus_password_123'
		cls.new_user = User.objects.create_user(username=cls.username, password=cls.password)

		cls.login_password = 'imaginary_password'
		cls.pass_obj = PasswordManager.objects.create(owner=cls.new_user, site_name='imaginary_name',
			site_url='http://example.com', login_name='imaginary_login', login_password=cls.login_password)

	def test_PasswordManagerForm_for_empty_data(self):
		form = PasswordManagerForm(data={})

		self.assertFalse(form.is_valid())
		self.assertIn('site_name', form.errors)
		self.assertIn('site_url', form.errors)
		self.assertIn('login_name', form.errors)
		self.assertIn('login_password', form.errors)

	def test_PasswordManagerForm_for_valid_data(self):
		form = PasswordManagerForm(
			data={
				'site_name': 'fake_name',
				'site_url': 'http://example.com',
				'login_name': 'fake_login',
				'login_password':'fake_password'
			})

		self.assertTrue(form.is_valid())

	def test_PasswordManagerForm_for_invalid_data(self):
		form = PasswordManagerForm(
			data={
				'site_name': 'fake_name'*4,
				'site_url': 'example',
				'login_name': 'fake_login'*4,
				'login_password': 'fake_password'*10
			})

		self.assertFalse(form.is_valid())
		self.assertIn('site_name', form.errors)
		self.assertIn('site_url', form.errors)
		self.assertIn('login_name', form.errors)
		self.assertIn('login_password', form.errors)

	def test_PasswordManagerForm_init_method_for_decrypting_login_password(self):
		form = PasswordManagerForm(instance=self.pass_obj)

		self.assertEqual(form.initial['login_password'], self.login_password)

	def test_PasswordManagerForm_save_method(self):
		site_name = 'fake_name'
		form = PasswordManagerForm(
			data={
				'site_name': site_name,
				'site_url': 'http://example.com',
				'login_name': 'fake_login',
				'login_password':'fake_password'
			})

		self.assertTrue(form.is_valid())

		form.save(owner=self.new_user)
		new_pass_obj = PasswordManager.objects.get(site_name=site_name)

		self.assertTrue(new_pass_obj.owner, self.new_user)


class ViewTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.username = 'bogus_name'
		cls.password = 'bogus_password_123'
		cls.new_user = User.objects.create_user(username=cls.username, password=cls.password)

		cls.login_password = 'imaginary_password'
		cls.pass_obj = PasswordManager.objects.create(owner=cls.new_user, site_name='imaginary_name',
			site_url='http://example.com', login_name='imaginary_login', login_password=cls.login_password)

	def test_password_manager_page_uses_correct_view_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		response = self.client.get(reverse('password_manager:password_manager'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, password_manager)

	def test_password_manager_page_render_correct_template_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		response = self.client.get(reverse('password_manager:password_manager'))

		self.assertTemplateUsed(response, 'password_manager/home.html')

	def test_password_manager_page_uses_redirect_for_anonymous_user(self):
		response = self.client.get(reverse('password_manager:password_manager'))

		self.assertRedirects(response, '/account/?next=/password_manager/', status_code=302, target_status_code=200)

	def test_password_manager_page_filter_queryset(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		new_user = User.objects.create_user(username='new_user', password='new_password')
		new_pass_obj = PasswordManager.objects.create(owner=new_user, site_name='fake_name',
			site_url='http://example.com', login_name='fake_login', login_password='fake_password')

		response = self.client.get(reverse('password_manager:password_manager'))

		self.assertIn(self.pass_obj, response.context['password_manager'])
		self.assertNotIn(new_pass_obj, response.context['password_manager'])

	def test_create_password_view_GET_request(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		response = self.client.get(
			reverse('password_manager:create_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json')

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertIn('site_name', response.content.decode('utf-8'))
		self.assertIn('login_password', response.content.decode('utf-8'))


	def test_create_password_view_valid_POST_request_for_logged_in_users(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		fake_name = 'fake_name'
		data = {
			'site_name': fake_name,
			'site_url': 'http://example.com',
			'login_name': 'fake_login',
			'login_password':'fake_password'
			}

		response = self.client.post(
			reverse('password_manager:create_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data=data)

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertEqual(len(response.context['password_manager'].filter(site_name=fake_name)), 1)
		self.assertEqual(len(PasswordManager.objects.filter(site_name=fake_name)), 1)
		self.assertFalse(response.context['password_manager_form'].errors)

	def test_create_password_view_valid_POST_request_for_anonymous_user(self):
		fake_name = 'fake_name'
		data = {
			'site_name': fake_name,
			'site_url': 'http://example.com',
			'login_name': 'fake_login',
			'login_password':'fake_password'
			}

		response = self.client.post(
			reverse('password_manager:create_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data=data)

		self.assertRedirects(response, '/account/?next=/password_manager/create_password', status_code=302, target_status_code=200)

		self.assertEqual('text/html; charset=utf-8', response['Content-Type'])


	def test_create_password_view_invalid_POST_request_for_logged_in_users(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		fake_name = 'fake_name'
		data = {
			'site_name': fake_name,
			'site_url': 'example',
			'login_name': 'fake_login',
			'login_password':''
			}

		response = self.client.post(
			reverse('password_manager:create_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data=data)

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])


		self.assertIn('site_url', response.context['password_manager_form'].errors)
		self.assertIn('login_password', response.context['password_manager_form'].errors)

		self.assertEqual(len(PasswordManager.objects.filter(site_name=fake_name)), 0)

	def test_edit_password_view_GET_request_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		response = self.client.get(
			reverse('password_manager:edit_password', kwargs={'password_pk': self.pass_obj.pk}),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json')

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertIn(self.pass_obj.site_name, response.content.decode('utf-8'))
		self.assertIn(self.pass_obj.login_name, response.content.decode('utf-8'))

	def test_edit_password_view_GET_request_for_anonymous_user(self):
		response = self.client.get(
			reverse('password_manager:edit_password', kwargs={'password_pk': self.pass_obj.pk}),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json')

		self.assertRedirects(
			response,
			'/account/?next=/password_manager/edit_password/{}'.format(self.pass_obj.pk),
			status_code=302,
			target_status_code=200)

	def test_edit_password_view_valid_POST_request_for_correct_logged_in_users(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		fake_name = 'fake_name'
		data = {
			'site_name': fake_name,
			'site_url': 'http://example.com',
			'login_name': 'fake_login',
			'login_password':'fake_password'
			}

		response = self.client.post(
			reverse('password_manager:edit_password', kwargs={'password_pk': self.pass_obj.pk}),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data=data)

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertEqual(response.context['password_manager'].get(site_name=fake_name).pk, self.pass_obj.pk)
		self.assertEqual(PasswordManager.objects.get(site_name=fake_name).pk, self.pass_obj.pk)
		self.assertFalse(response.context['password_manager_form'].errors)

	def test_edit_password_view_valid_POST_request_for_incorrect_logged_in_users(self):
		new_username = 'new_user'
		new_user_password = 'new_password'
		new_user = User.objects.create_user(username=new_username, password=new_user_password)

		self.client.login(username=new_username, password=new_user_password)
		self.assertIsInstance(auth.get_user(self.client), User)

		fake_name = 'fake_name'
		data = {
			'site_name': fake_name,
			'site_url': 'http://example.com',
			'login_name': 'fake_login',
			'login_password':'fake_password'
			}

		response = self.client.post(
			reverse('password_manager:edit_password', kwargs={'password_pk': self.pass_obj.pk}),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data=data)

		self.assertEqual(response.status_code, 404)

	def test_edit_password_view_invalid_POST_request_for_logged_in_users(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		fake_name = 'fake_name'
		data = {
			'site_name': fake_name,
			'site_url': 'example',
			'login_name': 'fake_login',
			'login_password':''
			}

		response = self.client.post(
			reverse('password_manager:edit_password', kwargs={'password_pk': self.pass_obj.pk}),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data=data)

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])


		self.assertIn('site_url', response.context['password_manager_form'].errors)
		self.assertIn('login_password', response.context['password_manager_form'].errors)

		self.assertEqual(len(PasswordManager.objects.filter(site_name=fake_name)), 0)

	def test_delete_password_view_GET_request_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		response = self.client.get(
			reverse('password_manager:delete_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json')

		self.assertEqual(response.status_code, 404)

	def test_delete_password_view_GET_request_for_anonymous_user(self):
		response = self.client.get(
			reverse('password_manager:delete_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json')

		self.assertRedirects(
			response,
			'/account/?next=/password_manager/delete_password',
			status_code=302,
			target_status_code=200)

	def test_delete_password_view_valid_POST_request_for_correct_logged_in_users(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		new_pass_obj = PasswordManager.objects.create(owner=self.new_user, site_name='fake_name',
			site_url='http://example.com', login_name='fake_login', login_password='fake_password')

		self.assertIn(new_pass_obj, PasswordManager.objects.all())

		data = dumps({"id": new_pass_obj.pk})

		response = self.client.post(
			reverse('password_manager:delete_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json',
			data=data)

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertEqual(len(response.context['password_manager'].filter(site_name=new_pass_obj.site_name)), 0)
		self.assertNotIn(new_pass_obj, PasswordManager.objects.all())

	def test_delete_password_view_valid_POST_request_for_incorrect_logged_in_users(self):
		new_username = 'new_user'
		new_user_password = 'new_password'
		new_user = User.objects.create_user(username=new_username, password=new_user_password)

		self.client.login(username=new_username, password=new_user_password)
		self.assertIsInstance(auth.get_user(self.client), User)

		data = dumps({"id": self.pass_obj.pk})

		response = self.client.post(
			reverse('password_manager:delete_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json',
			data=data)

		self.assertEqual(response.status_code, 404)

	def test_check_password_view_GET_request_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		response = self.client.get(
			reverse('password_manager:check_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json')

		self.assertEqual(response.status_code, 404)

	def test_check_password_view_GET_request_for_anonymous_user(self):
		response = self.client.get(
			reverse('password_manager:check_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json')

		self.assertRedirects(
			response,
			'/account/?next=/password_manager/check_password',
			status_code=302,
			target_status_code=200)

	def test_check_password_view_valid_POST_request(self):
		self.client.login(username=self.username, password=self.password)
		self.assertIsInstance(auth.get_user(self.client), User)

		data = dumps({"password": 'imagPAS7%&'})

		response = self.client.post(
			reverse('password_manager:check_password'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json',
			data=data)

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertIn('Bits of entropy', response.content.decode('utf-8'))
		self.assertIn('progress-bar', response.content.decode('utf-8'))


class ApiTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.username = 'bogus_name'
		cls.password = 'bogus_password_123'
		cls.new_user = User.objects.create_user(username=cls.username, password=cls.password)

		cls.login_password = 'imaginary_password'
		cls.site_name = 'imaginary_name'
		cls.pass_obj = PasswordManager.objects.create(owner=cls.new_user, site_name=cls.site_name,
			site_url='http://example.com', login_name='imaginary_login', login_password=cls.login_password)

	def test_PasswordManagerListAPIView_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)

		response = self.client.get(reverse('password_manager:api:list'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertIn(self.site_name, response.content.decode('utf-8'))

	def test_PasswordManagerListAPIView_for_anonymous_user(self):
		response = self.client.get(reverse('password_manager:api:list'))

		self.assertEqual(response.status_code, 403)
		self.assertEqual('application/json', response['Content-Type'])

	def test_PasswordManagerRetrieveAPIView_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)
		response = self.client.get(reverse('password_manager:api:retrieve', kwargs={'site_name': self.site_name}))

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertIn(self.site_name, response.content.decode('utf-8'))
		self.assertNotIn(str(self.pass_obj.login_password), response.content.decode('utf-8'))
		self.assertIn(self.login_password, response.content.decode('utf-8'))

	def test_PasswordManagerRetrieveAPIView_for_anonymous_in_user(self):
		response = self.client.get(reverse('password_manager:api:retrieve', kwargs={'site_name': self.site_name}))

		self.assertEqual(response.status_code, 403)
		self.assertEqual('application/json', response['Content-Type'])

	def test_PasswordManagerCreateAPIView_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)

		data = {
			'site_name': 'fake_name',
			'site_url': 'http://example.com',
			'login_name': 'fake_login',
			'login_password':'fake_password'
		}

		response = self.client.post(reverse('password_manager:api:create'), data=data)

		self.assertEqual(response.status_code, 201)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertIn(data['site_name'], PasswordManager.objects.all().values_list('site_name', flat=True))

	def test_PasswordManagerCreateAPIView_for_anonymous_user(self):
		data = {
			'site_name': 'fake_name',
			'site_url': 'http://example.com',
			'login_name': 'fake_login',
			'login_password':'fake_password'
		}

		response = self.client.post(reverse('password_manager:api:create'), data=data)

		self.assertEqual(response.status_code, 403)
		self.assertEqual('application/json', response['Content-Type'])

	def test_PasswordManagerUpdateAPIView_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)

		new_imaginary_name = 'new_imaginary_name'
		data = dumps({
			'site_name': new_imaginary_name,
			'site_url': 'http://example.com',
			'login_name': 'imaginary_login',
			'login_password':'imaginary_password'
		})

		response = self.client.put(
			reverse('password_manager:api:update', kwargs={'site_name': self.site_name}),
			content_type='application/json',
			data=data)

		self.assertEqual(response.status_code, 200)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertIn(new_imaginary_name, PasswordManager.objects.all().values_list('site_name', flat=True))
		self.assertIn(self.pass_obj.pk, PasswordManager.objects.all().values_list('pk', flat=True))

	def test_PasswordManagerUpdateAPIView_for_anonymous_user(self):
		new_imaginary_name = 'new_imaginary_name'
		data = dumps({
			'site_name': new_imaginary_name,
			'site_url': 'http://example.com',
			'login_name': 'imaginary_login',
			'login_password':'imaginary_password'
		})

		response = self.client.put(
			reverse('password_manager:api:update', kwargs={'site_name': self.site_name}),
			content_type='application/json',
			data=data)

		self.assertEqual(response.status_code, 403)
		self.assertEqual('application/json', response['Content-Type'])

		self.assertNotIn(new_imaginary_name, PasswordManager.objects.all().values_list('site_name', flat=True))
		self.assertIn(self.pass_obj.pk, PasswordManager.objects.all().values_list('pk', flat=True))

	def test_PasswordManagerDestroyAPIView_for_logged_in_user(self):
		self.client.login(username=self.username, password=self.password)

		new_site_name = 'fake_name'
		new_pass_obj = PasswordManager.objects.create(owner=self.new_user, site_name=new_site_name, 
			site_url='http://example.com', login_name='fake_login', login_password='fake_password')

		self.assertIn(new_site_name, PasswordManager.objects.all().values_list('site_name', flat=True))

		response = self.client.delete(reverse('password_manager:api:destroy', kwargs={'site_name': new_site_name}))

		self.assertEqual(response.status_code, 204)
		self.assertNotIn(new_site_name, PasswordManager.objects.all().values_list('site_name', flat=True))
	
	def test_PasswordManagerDestroyAPIView_for_anonymous_user(self):
		new_site_name = 'fake_name'
		new_pass_obj = PasswordManager.objects.create(owner=self.new_user, site_name=new_site_name, 
			site_url='http://example.com', login_name='fake_login', login_password='fake_password')

		self.assertIn(new_site_name, PasswordManager.objects.all().values_list('site_name', flat=True))

		response = self.client.delete(reverse('password_manager:api:destroy', kwargs={'site_name': new_site_name}))

		self.assertEqual(response.status_code, 403)
		self.assertIn(new_site_name, PasswordManager.objects.all().values_list('site_name', flat=True))
