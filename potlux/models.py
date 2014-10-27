from mongokit import Document

import datetime

class Idea(Document):
	structure = {
		'date_creation': datetime.datetime,
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

	required_fields = ['name', 'categories', 'contact']

	default_values = {
		'date_creation': datetime.datetime.utcnow
	}

	use_dot_notation = True
	