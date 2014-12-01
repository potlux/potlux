from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators

class LoginForm(Form):
	email = TextField('Email')
	password = PasswordField('Password')

class RegistrationForm(Form):
	email = TextField('Email', [
		validators.Required(),
		validators.length(min=6, max=50)
	])
	password = PasswordField('Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Confirm Password')