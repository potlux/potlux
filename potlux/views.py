from potlux import app
from models import *

from flask.ext.mongokit import MongoKit

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

app.config.from_object(__name__)

db = MongoKit(app)
db.register([Idea])

@app.route('/')
def home():
	return 'Welcome to potlux!'