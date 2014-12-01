from mongokit import Document
from flask.ext.login import UserMixin

import datetime

class User(Document, UserMixin):
	__database__ = 'potlux'
	__collection__ = 'users'

	structure = {
		'date_creation' : datetime.datetime,
		'email' : basestring,
		'password' : basestring,
		'name' : {
			'first' : basestring,
			'last' : basestring
		}
	}

	default_values = {
		'date_creation' : datetime.datetime.utcnow
	}

	required_fields = ['email', 'password']

	use_dot_notation = True

	def get_id(self):
		print "ID in model:", str(self._id)
		return str(self._id)

class BetaKey(Document):
	__database__ = 'potlux'
	__collection__ = 'beta_keys'

	structure = {
		'date_creation': datetime.datetime,
		'key' : basestring
	}

	required_fields = ['key']

	default_values = {
		'date_creation' : datetime.datetime.utcnow
	}

	use_dot_notation = True

class Idea(Document):
	__database__ = 'potlux'
	__collection__ = 'ideas'

	structure = {
		'date_creation': datetime.datetime,
		#'last_edit' : datetime.datetime,
		'name': basestring,
		'categories': [basestring],
		'university': basestring,
		'contact': {
			'name': basestring,
			'email': basestring,
		},
		'summary': basestring,
		'impact': basestring,
		'procedure': [basestring], # list of steps
		'results': { # mistakes made and lessons learned
			'positive': [basestring],
			'negative': [basestring],
		},
		'future': [basestring], # list of future plans
		'resources': { # lists of links
			'images': [basestring],
			'videos': [basestring],
			'websites': [basestring],
			'documents': [basestring]
		}
	}

	required_fields = ['name', 'categories', 'summary']

	default_values = {
		'date_creation': datetime.datetime.utcnow
	}

	use_dot_notation = True
	