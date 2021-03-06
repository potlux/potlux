from mongokit import Document, ObjectId
from flask.ext.login import UserMixin

import datetime

class User(Document, UserMixin):
	__database__ = 'potlux'
	__collection__ = 'users'

	structure = {
		'date_creation' : datetime.datetime,
		'email' : basestring,
		'password' : basestring,
		'verified' : bool,
		'name' : {
			'first' : basestring,
			'last' : basestring,
			'full' : basestring
		},
		'favorites' : [ObjectId] # ObjectId's of favorite projects.
	}

	default_values = {
		'date_creation' : datetime.datetime.utcnow
	}

	required_fields = ['email', 'password']

	use_dot_notation = True

	def get_id(self):
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
		'contacts': [{
			'name': basestring,
			'email': basestring,
		}],
		'summary': basestring,
		'impact': basestring,
		'procedure': basestring, 
		'results': basestring,
		'future': basestring, 
		'resources': { # lists of links
			'images': [{
				'image_id' : basestring,
				'thumbnail': basestring,
				'full_size' : basestring
			}],
			'project-image' : basestring,
			'videos': [basestring],
			'websites': [basestring],
			'documents': [basestring]
		},
		'owners' : [ObjectId],
		'status' : basestring
	}

	required_fields = ['name', 'summary']

	default_values = {
		'date_creation': datetime.datetime.utcnow
	}

	use_dot_notation = True
	