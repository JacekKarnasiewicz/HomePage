from django.contrib import auth
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import PasswordManager
from .utilities import CheckPassword

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
		pass_obj = CheckPassword('0123456789')

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
		pass_obj = CheckPassword('abcDEF01!@qweRTY34#$')

		self.assertAlmostEqual(pass_obj.get_bits_of_entropy(), 131.09, places=1)
		self.assertEqual(len(pass_obj.get_annotations()), 0)
		self.assertEqual(pass_obj.get_password_strength(), CheckPassword.password_strength_options[4])


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
	pass


class ViewTest(TestCase):
	pass
