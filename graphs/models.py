from __future__ import unicode_literals
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from graphspace.mixins import *

Base = declarative_base()

# ================== Table Definitions =================== #
