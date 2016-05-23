import uuid
from random import choice, randint, sample

def gen_password(length):
	vowels = list('euioay')
	consonants = list('qwrtpsdfghjklzxcvbnm')
	numbers = list('0123456789')

	result = ''
	num_count = randint(1, 3)
	while len(result) < length - num_count:
		result += choice([vowels, consonants][len(result) % 2])

	result += ''.join(sample(numbers, num_count))
	return result

def gen_salt(length):
	return uuid.uuid4().hex[:length]