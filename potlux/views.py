from potlux import app
from models import Idea

from flask import request, render_template, redirect, url_for
from mongokit import *
from bson.json_util import dumps

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

app.config.from_object(__name__)

connection = Connection()
connection.register([Idea])
db = connection.potlux

@app.route('/all')
def show_all():
	ideas = db.ideas.Idea.find()	
	return dumps([idea for idea in ideas])

@app.route('/new', methods=["POST", "GET"])
def new():
	if request.method == "POST":
		name = request.form["name"]
		categories = request.form["categories"].split(",")
		contact = {'name': request.form["contact_name"],
				   'email': request.form["contact_email"]}
		summary = request.form["summary"]

		new_idea = db.ideas.Idea()
		new_idea.name = name
		new_idea.categories = categories
		new_idea.contact = contact
		new_idea.summary = summary

		new_idea.save()
		return redirect(url_for('show_all'))
	else: 
		return render_template('new.html')

@app.route('/')
def home():
	return app.send_static_file('index.html')