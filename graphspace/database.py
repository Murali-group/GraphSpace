from contextlib import contextmanager

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from django.conf import settings


class Database(object):
	"""
		Create a database object to query from.
	"""

	def __init__(self):
		"""
			Constructor
		"""
		config = settings.DATABASES['default']
		self.engine = create_engine(''.join(
			['postgresql://', config['USER'], ':', config['PASSWORD'], '@', config['HOST'], ':', config['PORT'], '/', config['NAME']]), echo=False)
		# TODO: Find out what is the use of metadata and reflection.
		settings.BASE.metadata.create_all(self.engine)
		self.meta = sqlalchemy.schema.MetaData()
		self.meta.reflect(bind=self.engine)
		self.session = sessionmaker(bind=self.engine)

	@contextmanager
	def session_scope(self):
		"""
		Provide a transactional scope around a series of operations.
		This method could be used by test code or db scripts to run queries as transactions.

		with db.session_scope() as session:
			session.query(Widget).update({"q": 18})
			session.query(Widget).update({"q": 10})
		"""
		session = self.session()
		try:
			yield session
			session.commit()
		except:
			session.rollback()
			raise
		finally:
			session.close()
