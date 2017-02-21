from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import asc, desc

from django.utils.datetime_safe import datetime
from graphspace.utils import generate_uid
from graphspace.wrappers import with_session
from models import *


# TODO: Add documentation about exception raised.

@with_session
def find_uniprot_aliases(db_session, accession_number, alias_name, limit, offset, order_by=asc(UniprotAlias.accession_number)):
	query = db_session.query(UniprotAlias)

	if order_by is not None:
		query = query.order_by(order_by)

	filters = []
	if accession_number is not None:
		filters.append(UniprotAlias.accession_number.ilike(accession_number))

	if alias_name is not None:
		filters.append(UniprotAlias.alias_name.ilike(alias_name))

	if len(filters) > 0:
		query = query.filter(or_(*filters))

	total = query.count()

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()
