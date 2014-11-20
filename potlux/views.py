from potlux import app
from models import Idea

from flask import request, render_template, redirect, url_for, session, escape
from mongokit import *
import pymongo
from bson.json_util import dumps
from helpers import *

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

app.config.from_object(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = APP_ROOT + "/static/resources/user_images/"

connection = Connection()
connection.register([Idea])
db = connection.potlux

@app.route('/comingsoon')
def coming_soon():
	return 'Coming Soon' #app.send_static_file('comingsoon.html')

@app.route('/all')
def show_all():
	ideas = db.ideas.Idea.find()	
	return 'all' #dumps([idea for idea in ideas])

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
		return redirect(url_for('show_idea', id=str(new_idea._id)))
	else: 
		return render_template('submit.html')

@app.route('/idea/<id>', methods=["GET", "POST"])
def show_idea(id):
	idea = db.ideas.Idea.find_one({"_id" : ObjectId(id)})

	if request.method == "POST":		
		if 'imageUpload' in request.files:
			# handle image upload
			filename = process_image(request.files['imageUpload'])
			idea['resources']['images'].append(filename)
			idea.save()
		else:
			if 'summary' in request.form:
				print request.form['summary']
				idea['summary'] = request.form['summary']
			# for arg in request.args:
			# 	if isinstance(idea[arg], list):
			# 		idea[arg].append(request.args.get(arg))
			# 	else:
			# 		idea[arg] = request.args.get(arg)
			print "NEW IDEA:", idea
			idea.save()
			
	return render_template('project.html', idea=idea) #dumps(idea)

@app.route('/random')
def show_random():
	return dumps(db.ideas.Idea.find_random())

@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
    	# Create user
    	# log user in
        return redirect(url_for('home'))
    if 'user_email' in session:
    	return render_template('new_user.html', email=session['user_email'])
    else:
    	return render_template('new_user.html')

@app.route('/try/<beta_key>')
def beta():
	if is_allowed(beta_key):
		session['user_email'] = get_email(beta_key)
		redirect(url_for('new_user'))
	else:
		return "Potlux is still in beta, sign up here to get updates!"

@app.route('/')
def home():
	new_ideas = db.ideas.Idea.find(sort=[('date_creation', pymongo.DESCENDING)], max_scan=10)
	return render_template('index.html', ideas=new_ideas)
	