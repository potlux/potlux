from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, TextAreaField, validators
from potlux import db, uni_list
from werkzeug.security import check_password_hash

import requests, re

class AddNameForm(Form):
	first_name = TextField('FIRST NAME', validators = [validators.Required()])
	last_name = TextField('LAST NAME', validators = [validators.Required()])
	
class ProjectSubmitForm(Form):
	name = TextField('PROJECT NAME', validators = [validators.Required()])
	categories = TextField('CATEGORIES')
	university = TextField('UNIVERSITY', validators = [validators.Required()])
	first_name = TextField()
	last_name = TextField()
	website = TextField('WEBSITE')
	summary = TextAreaField('SUMMARY')

	def validate_website(self, field):
		if self.website.data:
			if 'http://' not in self.website.data:
				if requests.get('http://' + self.website.data).status_code is not 200:
					raise validators.ValidationError('Invalid link')
			elif requests.get(self.website.data).status_code is not 200:
				raise validators.ValidationError('Invalid link')

		# IP_REGEX = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"
		# if re.match(self.website.data, IP_REGEX):
		# 	raise validators.ValidationError('We do not accept IP Adresses!')
	def validate_university(self, field):
		if not self.university.data.lower() in uni_list:
			raise validators.ValidationError("We don't recognize this school!")

class EmailForm(Form):
    email = TextField('Email', validators = [validators.Email(), validators.Required()])

class PasswordForm(Form):
    password = PasswordField('Password', validators = [validators.Required()])

class LoginForm(Form):
	email = TextField('Email', [
		validators.Required()
	])

	password = PasswordField('Password', [
		validators.Required()
	])

	remember = BooleanField('Remember me')

	def validate_email(self, field):
		user = self.get_user()

		if user is None:
			raise validators.ValidationError('Email does not exist')

	def validate_password(self, field):
		user = self.get_user()

		if self.get_user() and not check_password_hash(user.password, self.password.data):
			raise validators.ValidationError('Invalid password')

	def get_user(self):
		return db.users.User.find_one({'email' : self.email.data})

class RegistrationForm(Form):
	first_name = TextField('First name', [
		validators.Required()
	])

	last_name = TextField('Last name', [
		validators.Required()
	])

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