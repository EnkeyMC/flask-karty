from sqlalchemy import Time, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from ..mixins import CRUDModel
from src.data.base import Base
from src.data.models.page import group_has_page
from ..database import db

user_has_group = Table('user_has_group', Base.metadata, Column('group_id', Integer, ForeignKey('group.id')), Column('user_id', Integer, ForeignKey('users.id')))


class Group(CRUDModel):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    group_name = Column(String(40), nullable=False,  index=True)
    access_time_from = Column(Time, nullable=True, index=True)
    access_time_to = Column(Time, nullable=True, index=True)
    users = relationship('User', secondary=user_has_group, backref='user')
    pages = relationship('Page', secondary=group_has_page, backref='groups')
        # Use custom constructor
    # pylint: disable=W0231
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def getGroupList():
        return db.session.query(Group.id, Group.group_name).all()