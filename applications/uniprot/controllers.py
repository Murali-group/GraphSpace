import bcrypt

from django.conf import settings
from django.core.mail import send_mail

import applications.uniprot.dal as db
from graphspace.exceptions import BadRequest, ErrorCodes
from graphspace.utils import generate_uid


def search_uniprot_aliases(request, accession_number=None, alias_name=None, limit=20, offset=0):
	total, uniprot_aliases = db.find_uniprot_aliases(request.db_session,
													 accession_number=accession_number,
													 alias_name=alias_name,
													 limit=limit,
													 offset=offset)

	return total, uniprot_aliases
