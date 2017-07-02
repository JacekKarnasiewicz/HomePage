from bisect import bisect
from math import log2
from re import search
from string import punctuation

# models => 8-32 char
# ommit adding list to db ! and checking all the possibilities

# using bisect is overkill, but i want to try something different from multiple if/elif/else statements


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
			self.annotations.add('Password must have at least 8 characters')
			self.password_strength = self._calculate_password_strength(self.bits_of_entropy)
			return

		# check lower and upper case characters
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


		self.bits_of_entropy = log2(self.pool_of_possible_characters) * self.password_length 
		self.password_strength = cls._calculate_password_strength(self.bits_of_entropy)

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
