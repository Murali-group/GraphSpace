from graphspace.exceptions import GraphSpaceError
from graphspace.exceptions.error_codes import *


class BadRequest(GraphSpaceError):
	"""
	The server cannot or will not process the request due to an apparent client error
	(e.g., malformed request syntax, too large size, invalid request message framing, or deceptive request routing)
	"""
	def __init__(self, request, error_code=ErrorCodes.Validation.BadRequest, args=None, msg=None):
		if msg is None:
			super(BadRequest, self).__init__(status=400, uri=request.path, msg=error_code[1].format(args) if args else error_code[1], code=error_code[0], method=request.method)
		else:
			super(BadRequest, self).__init__(status=400, uri=request.path, msg=msg, code=error_code[0], method=request.method)