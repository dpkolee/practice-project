
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed 
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from project1.model import User 
from flask_login import current_user

class RegistrationForm(FlaskForm):

	username = StringField('Username', validators=[DataRequired(), Length(min= 2, max=20)])
	email =  StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		
		user = User.query.filter_by(username = username.data).first()

		if user:
			raise ValidationError('Username is already taken!')

	def validate_email(self, email):
		
		user = User.query.filter_by(email = email.data).first()

		if user:
			raise ValidationError('Email is already taken!')


class LoginForm(FlaskForm):

	email =  StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

class UserUpdateForm(FlaskForm):

	username = StringField('Username', validators =  [DataRequired(), Length(min = 2, max = 20)])
	email = StringField('Email', validators = [DataRequired(), Email()])
	picture = FileField('Update profile pic', validators= [FileAllowed(['jpg','png'])])
	submit = SubmitField('Update')

	def validate_username(self, username):
		
		if username.data != current_user.username:

			user = User.query.filter_by(username = username.data).first()

			if user:
				raise ValidationError('Username is already taken!')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email = email.data).first()

			if user:
				raise ValidationError('Email is already taken!')

class RequestResetForm(FlaskForm):

	email = StringField('Email', validators = [DataRequired(), Email()])
	submit = SubmitField('Send Request')
	
	def validate_email(self, email):
		
		user = User.query.filter_by(email = email.data).first()

		if user is None:
			raise ValidationError('There is no account with that email. Please register first.')

class ResetPasswordForm(FlaskForm):

	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset')

