from flask import Flask
import os

app = Flask(__name__)

# set the secret key.  keep this really secret:
app.secret_key = os.urandom(24)

print "Running app..."

from potlux.views import *