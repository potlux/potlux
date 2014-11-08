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
		return render_template('submit.html')

@app.route('/idea/<id>', methods=["GET", "POST"])
def show_idea(id):
	idea = db.ideas.find_one({"_id" : ObjectId(id)})
	# if request.method == "POST":
		# update idea in database	
	return dumps(idea)

@app.route('/random')
def show_random():
	return dumps(db.ideas.Idea.find_random())

@app.route('/')
def home():
	return render_template('index.html')