import string
from django.utils.crypto import random


def generate_uid(size=20, chars=string.ascii_uppercase + string.digits):
	"""
		Generates an unique alphanumeric ID of specific size.

		:param size: Size of random string
		:param chars: Subset of characters to generate random string of
		:return string: Random string that adhere to the parameter properties
	"""
	return ''.join(random.choice(chars) for _ in range(size))


def json_success_response(status_code=200, message=""):
	return {
		"StatusCode": status_code,
		"Message": message
	}


def json_error_response(status_code=500, error=""):
	return {
		"StatusCode": status_code,
		"Error": error
	}