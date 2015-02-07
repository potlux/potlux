from potlux import app, db, login_required, login_user, logout_user
from forms import RegistrationForm, LoginForm, EmailForm, PasswordForm
from flask import request, render_template, redirect, url_for, session, escape, flash
from flask.ext.login import login_required, current_user
from mongokit import *
import pymongo
from bson.json_util import dumps
from helpers import *
from werkzeug.security import generate_password_hash

@app.route('/comingsoon')
def coming_soon():
	return app.send_static_file('comingsoon.html')

@app.route('/all')
# @login_required
def show_all():
	ideas = db.ideas.Idea.find()	
	return 'all' # dumps([idea for idea in ideas])

@app.route('/new', methods=["POST", "GET"])
# @login_required
def new():
	if request.method == "POST":
		name = request.form["name"].lower()
		categories = [cat.lower() for cat in request.form["categories"].split(",")]
		contact = {'name': request.form["first_name"] + " " + request.form["last_name"],
				   'email': request.form["email"]}
		summary = request.form["summary"]
		university = request.form["university"].lower()

		new_idea = db.ideas.Idea()
		new_idea.name = name
		new_idea.categories = categories
		new_idea.contact = contact
		new_idea.summary = summary
		new_idea.university = university

		if current_user.is_authenticated():
			new_idea.owner = current_user._id

		new_idea.save()
		return redirect(url_for('show_idea', id=str(new_idea._id)))
	else: 
		return render_template('submit.html')

@app.route('/idea/<id>', methods=["GET", "POST"])
def show_idea(id):
	idea = db.ideas.Idea.find_one({"_id" : ObjectId(id)})

	if request.method == "POST":
		print request.files
		if 'imageUpload' in request.files:
			# handle image upload
			filename = process_image(request.files['imageUpload'], id)
			print filename
			idea['resources']['images'].append(filename)
			idea.save()
		else:
			if 'summary' in request.form:
				idea['summary'] = request.form['summary']
			# for arg in request.args:
			# 	if isinstance(idea[arg], list):
			# 		idea[arg].append(request.args.get(arg))
			# 	else:
			# 		idea[arg] = request.args.get(arg)
			idea.save()
			
	return render_template('project.html', idea=idea)

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

		new_user = db.users.User()

		if db.users.User.find({'email' : user_email}).count() > 0:
			flash('An account with that email already exists!')
			form = RegistrationForm()
			return render_template('register.html', form=form)
		else:	
			new_user.email = user_email
			new_user.password = generate_password_hash(password)
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
	new_ideas = db.ideas.Idea.find().sort('date_creation', pymongo.DESCENDING).limit(10)
	return render_template('index.html', ideas=new_ideas)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')
	
