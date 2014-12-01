from potlux import app, db, login_required
from forms import RegistrationForm, LoginForm
from flask import request, render_template, redirect, url_for, session, escape
from mongokit import *
import pymongo
from bson.json_util import dumps
from helpers import *
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/comingsoon')
def coming_soon():
	return 'Coming Soon' #app.send_static_file('comingsoon.html')

@app.route('/all')
def show_all():
	ideas = db.ideas.Idea.find()	
	return 'all' # dumps([idea for idea in ideas])

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

@app.route('/login', methods=["GET", "POST"])
def login():
	form = LoginForm(request.form)
	if form.validate_on_submit():
		login_user(user) # login_user(user, remember=True)
		flash("Logged in succesfully")
		return redirect(request.args.get("next") or url_for('index'))
	return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm(request.form)
	if form.validate_on_submit():
		print "form validated"
    	# Create user
		user_email = form.email.data
		password = form.password.data
		# log user in
		print "email:", user_email
		print "password:", password
		return redirect(url_for('home'))
	if 'user_email' in session:
		print "email in session"
		return render_template('register.html', email=session['user_email'], form=form)
	else:
		print "going back to register"
		print form.errors
		return render_template('register.html', form=form)

@app.route('/try/<beta_key>')
def beta():
	if is_allowed(beta_key):
		session['user_email'] = get_email(beta_key)
		redirect(url_for('register'))
	else:
		return "Potlux is still in beta, sign up here to get updates!"

@app.route('/')
def home():
	new_ideas = db.ideas.Idea.find(sort=[('date_creation', pymongo.DESCENDING)], max_scan=10)
	return render_template('index.html', ideas=new_ideas)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
	