from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Integer, String

from ..database import db
from ..mixins import CRUDModel
from src.data.models.group import user_has_group, Group
from src.data.models.page import Page
from ..util import generate_random_token
from ...settings import app_config
from ...extensions import bcrypt

class User(CRUDModel, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    activate_token = Column(String(128), nullable=False, doc="Activation token for email verification")
    email = Column(String(64), nullable=False, unique=True, index=True, doc="The user's email address.")
    password_hash = Column(String(128))
    username = Column(String(64), nullable=False, unique=True, index=True, doc="The user's username.")
    verified = Column(Boolean(name="verified"), nullable=False, default=False)
    card_number = Column(String(32), unique=True, index=True, doc="Card access number")
    full_name = Column(String(40), unique=False, index=True, doc="Full name")
    group = relationship('Group', secondary=user_has_group, backref='user')

    # Use custom constructor
    # pylint: disable=W0231
    def __init__(self, **kwargs):
        self.activate_token = generate_random_token()
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def find_by_email(email):
        return db.session.query(User).filter_by(email=email).scalar()

    @staticmethod
    def find_by_username(username):
        return db.session.query(User).filter_by(username=username).scalar()

    # pylint: disable=R0201
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password, app_config.BCRYPT_LOG_ROUNDS)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_verified(self):
        " Returns whether a user has verified their email "
        return self.verified is True

    @staticmethod
    def find_by_number(card_number):
        return db.session.query(User).filter_by(card_number=card_number).scalar()

    def has_access(self, func_name):
        try:
            allowed_groups = db.session.query(Page).get(func_name).groups
        except AttributeError as e:
            print "[ERROR] This page is not in database."
            print e.message
            return False

        for g in self.group:
            if filter(lambda x: x.id == g.id, allowed_groups):
                return True
            elif g.group_name == 'superadmin':
                return True
        return False
