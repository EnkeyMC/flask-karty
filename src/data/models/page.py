from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from ..mixins import CRUDModel
from src.data.base import Base


group_has_page = Table('group_has_page', Base.metadata, Column('group_id', Integer, ForeignKey('group.id')), Column('id_page', String(80), ForeignKey('page.id')))


class Page(CRUDModel):
    __tablename__ = 'page'

    id = Column(String(80), primary_key=True)
    group = relationship('Group', secondary=group_has_page, backref='page')
        # Use custom constructor
    # pylint: disable=W0231
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
