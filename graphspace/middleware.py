from django.conf import settings


class SQLAlchemySessionMiddleware(object):
	def process_request(self, request):
		request.db_session = settings.db.session()

	def process_response(self, request, response):
		try:
			session = request.db_session
		except AttributeError:
			return response

		try:
			session.commit()
			session.close()
			return response
		except:
			session.rollback()
			session.close()
			raise

	def process_exception(self, request, exception):
		try:
			session = request.db_session
		except AttributeError:
			return
		session.rollback()
		session.close()



