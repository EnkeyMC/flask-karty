from sqlalchemy import func
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String,DateTime
from ..database import db
from ..mixins import CRUDModel

class Card(CRUDModel):
    __tablename__ = 'carddata'
    __public__ = ['id', 'card_number', 'time']

    id = Column(Integer, primary_key=True)
    card_number = Column(String(32),  index=True, doc="Card access number")
    id_user = Column(Integer, index=True)
    time = Column(DateTime)
    id_card_reader = Column(Integer)
        # Use custom constructor
    # pylint: disable=W0231
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def find_by_number(card_number):
        return db.session.query(Card).filter_by(card_number=card_number).scalar()
    @classmethod
    def stravenky(cls,month,card_number):
        narok=0
        form = db.session.query( func.strftime('%Y-%m-%d', cls.time).label("date"),func.max(func.strftime('%H:%M', cls.time)).label("Max"),\
                                 func.min(func.strftime('%H:%M', cls.time)).label("Min"),( func.max(cls.time) - func.min(cls.time)).label("Rozdil"))\
            .filter(func.strftime('%Y-%m', cls.time) == month).filter(cls.card_number == card_number).group_by(func.strftime('%Y-%m-%d', cls.time)).all()
        for n in form:
            if n.rozdil >= 3:
                narok = narok + 1
        return narok