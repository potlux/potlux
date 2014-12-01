from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, validators
from potlux import db
from werkzeug.security import check_password_hash

class LoginForm(Form):
	email = TextField('Email', [
		validators.Required()
	])

	password = PasswordField('Password')

	remember = BooleanField('Remember me')

	def validate_password(self, field):
		user = self.get_user()

		if user is None:
			raise validators.ValidationError('Email does not exist')

		if not check_password_hash(user.password, self.password.data):
			raise validators.ValidationError('Invalid password')

	def get_user(self):
		return db.users.User.find_one({'email' : self.email.data})


class RegistrationForm(Form):
	email = TextField('Email', [
		validators.Required(),
		validators.length(min=6, max=50),
		validators.Email()
	])

	def validate_email(self, field):
		if '.edu' not in self.email.data:
			raise validators.ValidationError('Please use a .edu email')

	password = PasswordField('Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Confirm Password')