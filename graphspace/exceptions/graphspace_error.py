import json


class GraphSpaceError(Exception):
	"""
		A generic 400 or 500 level exception from the GraphSpace API

		:param int status: the HTTP status that was returned for the exception.
		:param str uri: The URI that caused the exception.
		:param str msg: A human-readable message for the error.
		:param str method: The HTTP method used to make the request.
		:param int|None code: A GraphSpace-specific error code for the error. This is not available for all errors.
	"""

	def __init__(self, status, uri, msg="", code=None, method='GET'):
		self.uri = uri
		self.status = status
		self.msg = msg
		self.code = code
		self.method = method

	def __str__(self):

		""" Try to pretty-print the exception"""

		def get_uri(code):
			return "http://manual.graphspace.org/en/latest/Programmers_Guide.html#error-codes"

		return json.dumps({
			"status_code": self.status,
			"error_message": self.msg,
			"error_code": self.code,
			"error_details": get_uri(self.code),
			"http_request": "{0} {1}".format(self.method, self.uri)
		})

	def to_dict(self):
		return json.loads(str(self))

	def get_status(self):
		return self.status

	def get_message(self):
		return self.msg


class ValidationError(GraphSpaceError):
	def __init__(self, request, error_code):
		super(ValidationError, self).__init__(status=400, uri=request.path, msg=error_code[1], code=error_code[0], method=request.method)
