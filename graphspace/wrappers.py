def sqlalchemy_operation(inner):
	def inner_decorator(*args, **kwargs):
		# TODO: Add error logs and access logs and handle exceptions.
		try:
			inner(*args, **kwargs)
		except:
			raise
	return inner_decorator