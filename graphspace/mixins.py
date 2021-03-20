from sqlalchemy import Column, Integer, func, TIMESTAMP, Index
from sqlalchemy.ext.declarative import declared_attr
from django.utils.datetime_safe import datetime

"""
To share some functionality, such as a set of common columns, some common table options, or other mapped properties, across many classes.
For example:
	__table_args__ = {'mysql_engine': 'InnoDB'}
	__mapper_args__= {'always_refresh': True}
TODO: Find out what args need to be set for postgreSQL.
"""


class IDMixin(object):
	id = Column(Integer, primary_key=True, autoincrement=True, index=True, unique=True)


class TimeStampMixin(object):
	created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
	updated_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, onupdate=func.now())
