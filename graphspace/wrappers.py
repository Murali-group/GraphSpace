def with_session(inner):
	def inner_decorator(db_session, *args, **kwargs):
		# TODO: Add error logs and access logs and handle exceptions.
		try:
			result = inner(db_session, *args, **kwargs)
			db_session.flush()
			return result
		except:
			db_session.rollback()
			raise
	return inner_decorator


def atomic_transaction(inner):
	def inner_decorator(request, *args, **kwargs):
		try:
			result = inner(request, *args, **kwargs)
			request.db_session.flush()
			return result
		except:
			request.db_session.rollback()
			raise
	return inner_decorator