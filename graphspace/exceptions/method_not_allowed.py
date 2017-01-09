from graphspace.exceptions import GraphSpaceError
from graphspace.exceptions.error_codes import *


class MethodNotAllowed(GraphSpaceError):
	def __init__(self, request):
		super(MethodNotAllowed, self).__init__(status=405, uri=request.path, msg=ErrorCodes.Validation.MethodNotAllowed[1], code=ErrorCodes.Validation.MethodNotAllowed[0], method=request.method)