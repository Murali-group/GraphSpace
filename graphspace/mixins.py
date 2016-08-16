from sqlalchemy import Column, Integer, func, TIMESTAMP, Index
from sqlalchemy.ext.declarative import declared_attr
from django.utils.datetime_safe import datetime

"""
To share some functionality, such as a set of common columns, some common table options, or other mapped properties, across many classes.
"""


class GraphSpaceMixin(object):
    # TODO: Find out what args need to be set for postgreSQL.
    # __table_args__ = {'mysql_engine': 'InnoDB'}
    # __mapper_args__= {'always_refresh': True}

    id = Column(Integer, primary_key=True, autoincrement = True)
    created_at = Column(TIMESTAMP, default=datetime.now())
    updated_at = Column(TIMESTAMP, default=datetime.now())

    @declared_attr
    def __table_args__(cls):
        return (Index('%s_idx_%s' % (cls.__tablename__, 'id'), 'id'),)
