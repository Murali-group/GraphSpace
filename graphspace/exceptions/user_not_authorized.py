from graphspace.exceptions import GraphSpaceError
from graphspace.exceptions.error_codes import *


class UserNotAuthorized(GraphSpaceError):
	def __init__(self, request):
		super(UserNotAuthorized, self).__init__(status=403, uri=request.path, msg=ErrorCodes.Validation.UserNotAuthorized[1], code=ErrorCodes.Validation.UserNotAuthorized[0], method=request.method)
