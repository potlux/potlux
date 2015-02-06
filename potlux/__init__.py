from flask import Flask, abort
from models import Idea, User
from mongokit import *
from inflection import titleize
from itsdangerous import URLSafeTimedSerializer
from flask.ext.login import LoginManager, login_required, login_user, logout_user
from flask.ext.wtf.csrf import CsrfProtect
import flask.ext.security
import os, binascii

app = Flask(__name__)

# set the secret key.  keep this really secret:
app.secret_key = os.urandom(24)

print "Running app..."

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
WTF_CSRF_ENABLED = False

app.config.from_object(__name__)
app.config.from_object('potlux.config')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(APP_ROOT, "static", "resources", "user_images")

app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True

def generate_csrf_token():
    if '_csrf_token' not in session:
    	print "Generating CSRF token..."
        session['_csrf_token'] = binascii.hexlify(os.urandom(24))
   	print "Session contains CSRF token:", session['_csrf_token']
    return session['_csrf_token']

app.jinja_env.globals['len'] = len 
app.jinja_env.globals['titleize'] = titleize
app.jinja_env.globals['csrf_token'] = generate_csrf_token

connection = Connection()
connection.register([Idea, User])
db = connection.potlux

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])

from potlux.views import *

@login_manager.user_loader
def load_user(user_id):
	return db.users.User.find_one({'_id' : ObjectId(user_id)})

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        print "CSRF Token from form", request.form.get("_csrf_token")
        print "CSRF Token from session:", token
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

