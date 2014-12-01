from flask import Flask
from models import Idea, User
from mongokit import *
from flask.ext.login import LoginManager, login_required, login_user, logout_user
from flask.ext.wtf.csrf import CsrfProtect
import os

app = Flask(__name__)

# set the secret key.  keep this really secret:
app.secret_key = os.urandom(24)

print "Running app..."

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

app.config.from_object(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = APP_ROOT + "/static/resources/user_images/"

connection = Connection()
connection.register([Idea, User])
db = connection.potlux

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'register'

csrf = CsrfProtect()
csrf.init_app(app)

from potlux.views import *

@login_manager.user_loader
def load_user(user_id):
	return db.users.User.find_one({'_id' : ObjectId(user_id)})

