from potlux import app, db, login_required, login_user, logout_user, universities_trie
from forms import RegistrationForm, LoginForm, EmailForm, PasswordForm, ProjectSubmitForm
from flask import request, render_template, redirect, url_for, session, escape, flash, abort
from flask.ext.login import login_required, current_user
from mongokit import *
import pymongo
from bson.json_util import dumps
from helpers import *
from werkzeug.security import generate_password_hash
import os

@app.route('/comingsoon')
def coming_soon():
	return app.send_static_file('comingsoon.html')

@app.route('/all')
# @login_required
def show_all():
	ideas = db.ideas.Idea.find()	
	return 'all' # dumps([idea for idea in ideas])

@app.route('/new', methods=["POST", "GET"])
@login_required
def new():
	form = ProjectSubmitForm(request.form)
	if form.validate_on_submit():
		name = form.name.data.lower()
		categories = [cat.lower() for cat in form.categories.data.split(",")]
		contact = {'name': form.first_name.data + " " + form.last_name.data,
				   'email': current_user.email}
		summary = form.summary.data
		university = form.university.data.lower()
		website = sanitize_link(form.website.data.lower())

		new_idea = db.ideas.Idea()
		new_idea.name = name
		new_idea.categories = categories
		new_idea.contacts = [contact]
		new_idea.summary = summary
		new_idea.university = university
		new_idea.resources.websites = [website]

		if current_user.is_authenticated():
			new_idea.owners = [current_user._id]

		new_idea.save()
		return redirect(url_for('show_idea', id=str(new_idea._id)))
	else: 
		print form.errors
		return render_template('submit.html', form=form)

@app.route('/idea/<id>', methods=["GET", "POST"])
def show_idea(id):
	idea = db.ideas.Idea.find_one({"_id" : ObjectId(id)})
			
	return render_template('project.html', idea=idea)

@app.route('/idea/edit/<project_id>', methods=["GET", "POST"])
@login_required
def edit_idea(project_id):
	idea = db.ideas.Idea.find_one({"_id" : ObjectId(project_id)})
	if not current_user._id in idea.owners:
		flash("You're not allowed to do that!")
		return app.login_manager.unauthorized()

	if request.method == "POST":
		if 'imageUpload' in request.files:
			# handle image upload
			filenames = process_image(request.files['imageUpload'], project_id)
			print filenames
			idea['resources']['images'].append(filenames)
			idea.save()

		else:
			idea.impact = text_or_none(request.form['impact'].strip())
			idea.procedure = text_or_none(request.form['procedure'].strip())
			idea.future = text_or_none(request.form['future plans'].strip())
			idea.results = text_or_none(request.form['mistakes & lessons learned'].strip())
			idea.summary = text_or_none(request.form['summary'].strip())

			idea.save()

			return redirect(url_for('show_idea', id=project_id))

	return render_template('edit_project.html', idea=idea, idea_id=str(idea._id))

@app.route('/idea/edit/tags/<project_id>', methods=["POST", "DELETE"])
@login_required
def edit_project_tag(project_id):
	if request.method == "POST":
		new_category = request.form['new_cat'].strip().lower()
		if new_category:
			db.ideas.update({'_id' : ObjectId(project_id)},
				{'$addToSet' : {
					'categories' : new_category
				}})
		return redirect(url_for('edit_idea', project_id=project_id))
	if request.method == "DELETE":
		delete_cat = request.args.get('del_cat')
		db.ideas.update({'_id' : ObjectId(project_id)},
			{'$pull' : {
				'categories' : delete_cat
			}})
		return 'Success!'
	abort(404)

@app.route('/idea/edit/websites/<project_id>', methods=["POST", "DELETE"])
@login_required
def edit_project_website(project_id):
	if request.method == "POST":
		new_website = request.form['new_site'].strip().lower()
		if new_website:
			db.ideas.update({'_id' : ObjectId(project_id)},
				{'$addToSet' : {
					'resources.websites' : new_website
				}})
		return redirect(url_for('edit_idea', project_id=project_id))
	if request.method == "DELETE":
		delete_site = request.args.get('del_site')
		db.ideas.update({'_id' : ObjectId(project_id)},
			{'$pull' : {
				'resources.websites' : delete_site
			}})
		return 'Success!'
	abort(404)

##
# Route to search by tag.
##
@app.route('/search')
@app.route('/search/<tag>')
def search(tag=None):
	ideas = None
	search_by = request.args.get('search_type')
	print "Searching by:", search_by
	if not tag:
		tag = request.args.get('search')
	
	if search_by == "recent":
		ideas = db.ideas.Idea.find().sort('date_creation', pymongo.DESCENDING).limit(10)
	elif search_by == "category":
		print "searching by category"
		ideas = db.ideas.Idea.find({"categories" : { "$all" : [tag]}})
	elif search_by == "university":
		ideas = db.ideas.Idea.find({"university" : tag})
	else:
		print "didn't find a match"
		ideas = db.ideas.Idea.find().sort('date_creation', pymongo.DESCENDING).limit(10)
	
	return render_template('index.html', ideas=ideas)

@app.route('/random')
@login_required
def show_random():
	return dumps(db.ideas.Idea.find_random())

@app.route('/login', methods=["GET", "POST"])
def login():
	form = LoginForm(request.form)
	if form.validate_on_submit():
		print "form validated"
		login_user(form.get_user(), remember=form.remember.data) # login_user(user, remember=True)
		flash("Logged in succesfully")
		return redirect(request.args.get("next") or url_for('home'))
	return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm(request.form)
	if form.validate_on_submit():
    	# Create user
		user_email = form.email.data
		password = form.password.data

		first_name = form.first_name.data
		last_name = form.last_name.data

		new_user = db.users.User()

		if db.users.User.find({'email' : user_email}).count() > 0:
			flash('An account with that email already exists!')
			form = RegistrationForm()
			return render_template('register.html', form=form)
		else:	
			new_user.email = user_email
			new_user.password = generate_password_hash(password)
			new_user.name.first = first_name
			new_user.name.last = last_name
			new_user.verfied = False
			new_user.save()

		# log user in
		send_verification_email(new_user)
		login_user(new_user)
		flash('Check your email for verification!')
		return redirect(url_for('home'))
	else:
		return render_template('register.html', form=form)

@app.route('/verify/<token>')
def verify(token):
    try:
        email = ts.loads(token, salt=app.config['EMAIL_CONFIRM_KEY'], max_age=86400)
    except:
        abort(404)

    user = db.users.User.find_one({'email' : email})
    user.verified = True
    user.save()
    login_user(user)
    return redirect(url_for('home'))

@app.route('/reset', methods=["GET", "POST"])
def reset_password():
	print "reseting password"
	form = EmailForm()
	if form.validate_on_submit():
		user = db.users.User.find_one({'email' : form.email.data})

		subject = "Potlux password reset requested"
		token = ts.dumps(user.email, salt=app.config['RECOVER_KEY'])
		recover_url = url_for('reset_with_token', token=token, _external=True)
		body = render_template('email/reset.txt', url=recover_url)
		html = render_template('email/reset.html', url=recover_url)
		send_email(subject, app.config['FROM_EMAIL_ADDRESS'], [user.email], body, html)
		
		flash('Check your email for password reset link')
		return redirect(url_for('home'))
	return render_template('reset.html', form=form)

@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt=app.config['RECOVER_KEY'], max_age=86400)
    except:
        abort(404)

    form = PasswordForm()

    if form.validate_on_submit():
        user = db.users.User.find_one({'email' : email})
        user.password = generate_password_hash(form.password.data)
        user.save()

        return redirect(url_for('login'))
    return render_template('reset_with_token.html', form=form, token=token)

@app.route('/try/<beta_key>')
def beta():
	if is_allowed(beta_key):
		session['user_email'] = get_email(beta_key)
		redirect(url_for('register'))
	else:
		return "Potlux is still in beta, sign up here to get updates!"

@app.route('/')
# @login_required
def home():
	new_ideas = db.ideas.Idea.find().sort('date_creation', pymongo.DESCENDING).limit(20)
	return render_template('index.html', ideas=new_ideas)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact', methods=["GET", "POST"])
def contact():
	if request.method == "POST":
		name = request.form['name']
		email = request.form['mail']
		message = request.form['comment']

		subject = 'Potlux Feedback'
		sender = app.config['FROM_EMAIL_ADDRESS']
		recipients = [app.config['FROM_EMAIL_ADDRESS']]
		text_body = render_template('email/feedback.txt', 
			message=message, name=name, email=email)
		html_body = render_template('email/feedback.html', 
			message=message, name=name, email=email)

		send_email(subject, sender, recipients, text_body, html_body)

		flash('Thanks for your feedback!')
	return render_template('contact.html')

@app.route('/schools_list')
def schools():
	prefix = request.args.get('term')
	return dumps(universities_trie.keys(prefix))
	
