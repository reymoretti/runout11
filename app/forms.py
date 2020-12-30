from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import Customer, Foodseller
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed

class RegistrationFormCustomer(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Customer.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already used, choose a different one')

    def validate_email(self, email):
        user = Customer.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already used, choose a different one')

    def validate_password(self, password):
        passw = password.data
        c_upperCase = 0
        c_lowerCase = 0
        c_number = 0

        for i in passw:
            if i.isdigit():
                c_number = c_number + 1
            elif i.isupper():
                c_upperCase = c_upperCase + 1
            elif i.islower():
                c_lowerCase = c_lowerCase + 1

        if c_number == 0:
            raise ValidationError('Make sure your password has at least one number in it')

        elif c_upperCase == 0:
            raise ValidationError('Make sure your password has at least one upper case character in it')

        elif c_lowerCase == 0:
            raise ValidationError('Make sure your password has at least one lower case character in it')


class RegistrationFormFoodseller(FlaskForm):
    foodsellerName = StringField('Store Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=20)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=9,max=10)])
    opening_hours = StringField('Opening Hours', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_FoodsellerName(self, FoodsellerName):
        user = Foodseller.query.filter_by(foodsellerName=FoodsellerName.data).first()
        if user:
            raise ValidationError('Username already used, choose a different one')

    def validate_email(self, email):
        user = Foodseller.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already used, choose a different one')

    def validate_password(self, password):
        passw = password.data
        c_upperCase = 0
        c_lowerCase = 0
        c_number = 0

        for i in passw:
            if i.isdigit():
                c_number = c_number + 1
            elif i.isupper():
                c_upperCase = c_upperCase + 1
            elif i.islower():
                c_lowerCase = c_lowerCase + 1

        if c_number == 0:
            raise ValidationError('Make sure your password has at least one number in it')

        elif c_upperCase == 0:
            raise ValidationError('Make sure your password has at least one upper case character in it')

        elif c_lowerCase == 0:
            raise ValidationError('Make sure your password has at least one lower case character in it')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateCustomerAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=20)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Customer.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already used, choose a different one')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Customer.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already used, choose a different one')

class UpdateFoodsellerAccountForm(FlaskForm):
    foodsellerName = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=20)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=9, max=10)])
    opening_hours = StringField('Opening Hours', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_foodsellerName(self, foodsellerName):
        if foodsellerName.data != current_user.foodsellerName:
            user = Foodseller.query.filter_by(foodsellerName=foodsellerName.data).first()
            if user:
                raise ValidationError('Name already used, choose a different one')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Foodseller.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already used, choose a different one')

class OfferForm(FlaskForm):
    offer_name = StringField('Name of the product', validators=[DataRequired()])
    brand = StringField('Brand of the product', validators=[DataRequired()])
    description = StringField('Optional description')
    exp_date = StringField('Expiring date', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    percentage_discount = IntegerField('Discount percentage (without "%") ', validators=[DataRequired()])
    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Post')

    def validate_email(self, email):
        user = Customer.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email, you must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
