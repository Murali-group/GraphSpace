class ErrorCodes(object):
	"""
		A set of constants representing errors.  Error messages can change, but the codes will not.
		See the source for a list of all errors codes.
		Codes can be used to check for specific errors.
	"""
	class API(object):
		MethodNotAllowed = (1000, "Incoming request is not allowed")

	class VIEW(object):
		UserPasswordMisMatch = (2000, "User/Password not recognized")
