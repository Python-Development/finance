from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import InputRequired, Length, equal_to, NumberRange, DataRequired


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=10)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=30)])
    confirmPassword = PasswordField('confirmPassword', validators=[InputRequired(), equal_to('password')])


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=10)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=30)])


class QuoteForm(FlaskForm):
    symbol = StringField('symbol', validators=[InputRequired(), Length(max=6)])


class BuyForm(FlaskForm):
    symbol = StringField('symbol', validators=[InputRequired(), Length(max=10)])
    number = IntegerField('number', default=1, validators=[DataRequired(), NumberRange(min=1)])


class SellForm(FlaskForm):
    # select_shares = SelectField('select_shares', validators=[InputRequired()], choices=choices())
    number = IntegerField('number', default=1, validators=[DataRequired(), NumberRange(min=1)])