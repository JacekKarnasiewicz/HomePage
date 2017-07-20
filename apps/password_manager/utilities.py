from bisect import bisect
from math import log2
from re import IGNORECASE, search
from string import punctuation


class CheckPassword(object):
	breakpoints = [40, 60, 80, 100]
	password_strength_options = ['very weak', 'weak', 'semi-safe', 'good', 'strong']

	def __init__(self, password):
		self.password = password
		self.password_length = len(password)
		self.pool_of_possible_characters = 0
		self.bits_of_entropy = 0
		self.annotations = set()
		self.password_strength = ''

		self._calculate()

	def _calculate(self):
		cls = self.__class__

		# check password length
		if self.password_length < 8:
			self.annotations.add('Password should have at least 8 characters')
			self.password_strength = cls._calculate_password_strength(self.bits_of_entropy)
			return

		# check lower case characters
		if search('[a-z]', self.password):
			self.pool_of_possible_characters += 26

		else:
			self.annotations.add('Password should have at least one lower case character')

		# check upper case characters
		if search('[A-Z]', self.password):
			self.pool_of_possible_characters += 26			
		else:
			self.annotations.add('Password should have at least one upper case character')

		# check digits characters
		if search('[0-9]', self.password):
			self.pool_of_possible_characters += 10
		else:
			self.annotations.add('Password should have at least one digit character')

		# check special characters
		if search('[{}]'.format(punctuation), self.password):
			self.pool_of_possible_characters += len(punctuation)	# for now +32
		else:
			self.annotations.add(
				'Password should have at least one special character: {}'.format(punctuation))


		# UPDATE AFTER CONVERSATION WITH ERIC
		# 1) If we want exclude 100% of the passwords from 'top 100K list of passwords' we can
		# just change the length of the password to 16 characters - but it's very poor idea and
		# nobody(especially clients) want to think up long passwords

		# 2) But If we want to support our previous idea with regular expression, 8 characters for
		# password and omit checking whole list and we don't want to hardcode special cases, we can add
		# additional checks and accept the fact that we can't have 100% exclusion, because of the passwords like:
		# 'L58jkdjP!', 'xxPa33bq.aDNA', Jhon@ta2011 - I have no idea why that kind of passwords are
		# very frequent?! - some say, that they are frequently used by french people, but it is impossible to
		# create some sort of regular expression, especial if we take a look at the 'top 1 million list of
		# passwords', we can find passwords like:
		# 'V#jXFPb5_fkh1AHK', '!v_J#zCws9mjI107', 'YNyty@e9ELu@uX' or '0!g2437k8D#NTzUe' - why that kind of
		# passwords are very frequent?!

		# 3) If we want to exclude 100% of the passwords from the 'top 100K and 1M list of passwords' we can
		# combine regular expressions with checking pre filtered list in our database. Every time when we update
		# our code repository we can run custom 'django management command' that checks and update current
		# 'top 100K and 1M list of passwords' and only store in our database those that are not excluded by
		# our regular expressions - so our list will be relatively short.

		# ADDITIONAL CHECKS
		# (with additional checks we drop from 12 to 3 passwords that pass our validation from 'top 100K passwords')

		# mutation of the word 'password'
		if search('password', self.password.lower().replace('@', 'a').replace('0', 'o').replace('$', 's')):
			self.annotations.add("Password shouldn't include mutation of word 'password'")

		# common substrings
		if search('(wsx)|(qaz)|(zxc)|(asd)|(qwe)|(123)', self.password, flags=IGNORECASE):
			self.annotations.add(
				"Password shouldn't include combination of substrings: wsx, qaz, zxc, asd, qwe and 123")



		self.bits_of_entropy = log2(self.pool_of_possible_characters) * self.password_length 
		self.password_strength = cls._calculate_password_strength(self.bits_of_entropy)

	# using bisect is overkill, but i want to try something different from multiple if/elif/else statements
	@classmethod
	def _calculate_password_strength(cls, bits_of_entropy):
		return cls.password_strength_options[bisect(cls.breakpoints, bits_of_entropy)]

	# def create_context_dictionary(self):
	# 	pass

	def get_bits_of_entropy(self):
		return self.bits_of_entropy

	def get_annotations(self):
		return list(self.annotations)

	def get_password_strength(self):
		return self.password_strength


