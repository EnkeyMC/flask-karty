from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from ..database import db
from ..mixins import CRUDModel


class Card(CRUDModel):
    __tablename__ = 'card'

    card_number = Column(String(32),  index=True, doc="Card access number")
    id_user = Column(Integer, ForeignKey('users.id'), index=True, nullable=True)
        # Use custom constructor
    # pylint: disable=W0231
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def find_by_number(card_number):
        return db.session.query(Card).filter_by(card_number=card_number).scalar()
