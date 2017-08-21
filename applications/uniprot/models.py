from __future__ import unicode_literals

from sqlalchemy import ForeignKeyConstraint, text

from applications.users.models import *
from django.conf import settings
from graphspace.mixins import *

Base = settings.BASE

# ================== Table Definitions =================== #


class UniprotAlias(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'uniprot_alias'

	accession_number = Column(String, nullable=False)
	alias_source = Column(String, nullable=False)
	alias_name = Column(String, nullable=False)

	constraints = (
		UniqueConstraint('accession_number', 'alias_source', 'alias_name', name='_uniprot_alias_uc_accession_number_alias_source_alias_name'),
	)

	indices = (
		Index('uniprot_alias_idx_accession_number', text("accession_number gin_trgm_ops"), postgresql_using="gin"),
		Index('uniprot_alias_idx_alias_name', text("alias_name gin_trgm_ops"), postgresql_using="gin"),
	)

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls, **kwargs):
		return {
			# 'id': cls.id,
			'id': cls.accession_number,
			'alias_source': cls.alias_source,
			'alias_name': cls.alias_name,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}
