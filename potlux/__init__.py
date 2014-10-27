from flask import Flask
app = Flask(__name__)

print "Running app..."

from potlux.views import *