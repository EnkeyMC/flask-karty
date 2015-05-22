from sqlalchemy import Time, ForeignKey, Table
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from ..mixins import CRUDModel
from src.data.base import Base

access_identifier = Table('access_identifier', Base.metadata, Column('access_id', Integer, ForeignKey('access.id')), Column('user_id', Integer, ForeignKey('users.id')))


class Access(CRUDModel):
    __tablename__ = 'access'

    id = Column(Integer, primary_key=True)
    access_name = Column(String(40), nullable=False,  index=True)
    access_time_from = Column(Time, nullable=True, index=True)
    access_time_to = Column(Time, nullable=True, index=True)
        # Use custom constructor
    # pylint: disable=W0231
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)