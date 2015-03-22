import re
from datetime import datetime,date

from flask_wtf import Form
from wtforms.fields import BooleanField, TextField, PasswordField,SelectField
from wtforms_components  import TimeField
from wtforms.validators import EqualTo, Email, InputRequired, Length

from ..data.models import User
from ..fields import Predicate

def email_is_available(email):
    if not email:
        return True
    return not User.find_by_email(email)

def username_is_available(username):
    if not username:
        return True
    return not User.find_by_username(username)

def safe_characters(s):
    " Only letters (a-z) and  numbers are allowed for usernames and passwords. Based off Google username validator "
    if not s:
        return True
    return re.match(r'^[\w]+$', s) is not None
def isnumeric(s):
    " Only letters (a-z) and  numbers are allowed for usernames and passwords. Based off Google username validator "
    if not s:
        return True
    return re.match(r'^[012345679]+$', s) is not None

class EmailForm(Form):
    email = TextField('Email Address', validators=[
        Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])

class LoginForm(EmailForm):
    password = PasswordField('Password', validators=[
        InputRequired(message="You can't leave this empty")
    ])

    remember_me = BooleanField('Keep me logged in')

class ResetPasswordForm(Form):
    password = PasswordField('New password', validators=[
        EqualTo('confirm', message='Passwords must match'),
        Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])

    confirm = PasswordField('Repeat password')

class RegistrationForm(Form):
    username = TextField('Choose your username', validators=[
        Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Predicate(username_is_available,
                  message="An account has already been registered with that username. Try another?"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])

    email = TextField('Your email address', validators=[
        Predicate(email_is_available, message="An account has already been reigstered with that email. Try another?"),
        Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])

    password = PasswordField('Create a password', validators=[
        Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])

class EditUserForm(Form):
    username = TextField('Choose your username', validators=[
        Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])

    email = TextField('Your email address', validators=[
        Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])

    password = PasswordField('Create a password', validators=[
        Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])

    card_number = TextField('You access Card  number', validators=[
        Predicate(isnumeric, message="Pleas only number value is possible")

    ])
    full_name = TextField('Full Name', validators=[

        InputRequired(message="You can't leave this empty")
    ])
    access=SelectField('Access',choices=[('A', 'SuperAdmin'), ('B', 'Admin'), ('U', 'User')])

class Editdate(Form):
    #startdate = TimeField('Datum prichodu')
    enddate = TimeField('Datum odchodu')
    startdate = TimeField('Datum prichodu')
    #enddate = TextField('Datum odchodu')


class MonthInsert(Form):
    datum=datetime.today()
    months_choices = []
    for i in range(9,13):
        months_choices.append((datetime(datum.year-1, i, 1).strftime('%Y-%m'), datetime(datum.year-1, i, 1).strftime('%Y-%m')))
    for i in range(1,13):
        months_choices.append((datetime(datum.year, i, 1).strftime('%Y-%m'), datetime(datum.year, i, 1).strftime('%Y-%m')))
    for i in range(1,3):
        months_choices.append((datetime(datum.year+1, i, 1).strftime('%Y-%m'), datetime(datum.year+1, i, 1).strftime('%Y-%m')))
    month = SelectField('Vyber', default=datetime(datum.year, datum.month, 1).strftime('%Y-%m'),choices = months_choices)
