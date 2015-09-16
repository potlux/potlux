from potlux import app, db, login_required, login_user, logout_user, universities_trie, APP_ROOT
from project_controller import ProjectController
from forms import RegistrationForm, LoginForm, EmailForm, PasswordForm, ProjectSubmitForm, AddNameForm
from flask import request, render_template, redirect, url_for, session, escape, flash, abort
from flask.ext.login import login_required, current_user
from mongokit import *
import pymongo
from bson.json_util import dumps, loads
from helpers import *
from werkzeug.security import generate_password_hash
import os

@app.route('/comingsoon')
def coming_soon():
	return app.send_static_file('comingsoon.html')

@app.route('/all')
# @login_required
def show_all():
	# ProjectController.show_all()
	ideas = db.ideas.Idea.find()
	return 'all' # dumps([idea for idea in ideas])

@app.route('/new', methods=["POST", "GET"])
@login_required
def new():
	p = ProjectController(request)
	return p.create()

@app.route('/idea/delete/<project_id>')
def delete_idea(project_id):
	p = ProjectController(request)
	return p.delete(project_id)

@app.route('/idea/<project_id>', methods=["GET", "POST"])
def show_idea(project_id):
	p = ProjectController(request)
	return p.show(project_id)

@app.route('/idea/edit/<project_id>', methods=["GET", "POST"])
@login_required
def edit_idea(project_id):
	p = ProjectController(request)
	return p.edit(project_id)

@app.route('/idea/edit/remove/image/<project_id>', methods=["DELETE"])
def delete_project_image(project_id):
	p = ProjectController(request)
	return p.delete_project_image(project_id)

@app.route('/idea/edit/project-image/<project_id>', methods=["PUT"])
def set_project_image(project_id):
	p = ProjectController(request)
	return p.set_project_image(project_id)

@app.route('/idea/edit/tags/<project_id>', methods=["POST", "DELETE"])
@login_required
def edit_project_tag(project_id):
	p = ProjectController(request)
	return p.edit_project_tag(project_id)

@app.route('/idea/edit/websites/<project_id>', methods=["POST", "DELETE"])
@login_required
def edit_project_website(project_id):
	p = ProjectController(request)
	return p.edit_project_website(project_id)

##
# Deletes or adds contact to a project.
# Responds to url /idea/edit/contacts/<project_id>
# Form value: contact_email=<contact_email>
#
# If the email entered is associated with an account on Potlux, that user will be
# added/deleted as an owner of the project as well as his/her contact info being
# added to the project. An email will be sent to the user being added/deleted to
# confirm the action before any change is made in the database. This email will link
# to /idea/edit/contacts/confirm/<token>, which updates project in the database when
# clicked.
##
@app.route('/idea/edit/contacts/<project_id>', methods=["POST", "DELETE"])
@login_required
def edit_project_contacts(project_id):
	p = ProjectController(request)
	return p.edit_project_contacts(project_id)

@app.route('/idea/edit/contacts/confirm/<token>')
def contact_confirm(token):
	try:
		token_string = ts.loads(token, salt=app.config['EMAIL_CONFIRM_KEY'], max_age=86400)
	except:
		abort(404)

	email = token_string.split('&')[0]
	project_id = token_string.split('&')[1]

	added_user = db.users.User.find_one({'email' : email})
	if added_user:
		db.ideas.update({'_id' : ObjectId(project_id)},
			{'$addToSet' : {
				'contacts' : {
					'name' : added_user.name.full,
					'email' : added_user.email
				},
				'owners' : added_user._id
			}})
	else:
		db.ideas.update({'_id' : ObjectId(project_id)},
			{'$addToSet' : {
				'contacts' : {
					'name' : '',
					'email' : email
				}
			}})
	flash('You have been added as a contact for this project.')
	return redirect(url_for('show_idea', project_id=project_id))

##
# Route to search by tag.
##
@app.route('/search')
def search(query=None):
	ideas = None
	search_by = request.args.get('search_type')
	if not query:
		query = request.args.get('search')

	if search_by == "recent":
		ideas = db.ideas.Idea.find({'status' : 'active'}).sort('date_creation', pymongo.DESCENDING)
	elif search_by == "tag":
		ideas = db.ideas.Idea.find({
			"status" : "active",
			"categories" : { "$all" : [query.lower()]}
		}).sort('date_creation', pymongo.DESCENDING)
	elif search_by == "university":
		ideas = db.ideas.Idea.find({
			"university" : query.lower(),
			"status" : "active"
		}).sort('date_creation', pymongo.DESCENDING)
		if ideas.count() <= 0:
			search_terms = universities_trie.keys(query.lower())
			print "Search terms", search_terms
			ideas = db.ideas.Idea.find({
				"university" : {
					"$in" : search_terms
				},
				"status" : "active"
			}).sort('date_creation', pymongo.DESCENDING)
	else:
		ideas = db.ideas.Idea.find({"status" : "active"}).sort('date_creation', pymongo.DESCENDING)

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
			new_user.name.full = first_name + ' ' + last_name
			new_user.verfied = False
			new_user.save()

		# log user in
		send_verification_email(new_user)
		login_user(new_user)
		flash('Check your email for verification!')
		return redirect(url_for('home'))
	else:
		return render_template('register.html', form=form)

@app.route('/user/<user_id>')
def show_user(user_id):
	user = db.users.User.find_one({'_id' : ObjectId(user_id)})
	print user
	favorites = []
	if user.favorites:
		favorites = db.ideas.Idea.find({
			'_id' : {
				'$in' : user.favorites
			}
		})
	print favorites
	print "RENDERING TEMPLATE"
	return render_template('profile.html', user=user, favorites=favorites)

##
# TODO: add user authentication for this route.
##
@app.route('/user/<user_id>/add/favorite', methods=['PUT'])
def add_favorite(user_id):
	project_id = ObjectId(request.args.get('project_id'))

	if db.users.find({'_id' : ObjectId(user_id), 'favorites' : project_id}).count() > 0:
		db.users.update({'_id' : ObjectId(user_id)},
			{'$pull' : {
				'favorites' : project_id
			}})
	else:
		db.users.update({'_id' : ObjectId(user_id)},
			{'$addToSet' : {
				'favorites' : project_id
			}})
	return 'Success!'

@app.route('/verify/<token>')
def verify(token):
    try:
        email = ts.loads(token, salt=app.config['EMAIL_CONFIRM_KEY'], max_age=86400)
    except:
        abort(404)

    user = db.users.User.find_one({'email' : email})
    user.verified = True
    user.save()

    # Find all projects with this person as a contact and add this user as an owner.
    print db.ideas.update({'contacts.email' : user.email}, {
    		'$addToSet' : {
    			'owners' : user._id
    		}}, multi=True)
    print db.ideas.update({'contacts.email' : user.email}, {
			'$set' : {
    			'contacts.$.name' : user.name.full
    		}}, multi=True)


    login_user(user)
    return redirect(url_for('home'))

@app.route('/reset', methods=["GET", "POST"])
def reset_password():
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
	if current_user.is_authenticated() and not current_user.name.full:
		return redirect(url_for('add_name'))
	new_ideas = db.ideas.Idea.find({'status' : 'active'}).sort('date_creation', pymongo.DESCENDING)
	return render_template('index.html', ideas=new_ideas)

@app.route('/add_name', methods=["GET", "POST"])
@login_required
def add_name():
	form = AddNameForm(request.form)
	if form.validate_on_submit():
		first_name = form.first_name.data
		print first_name
		last_name = form.last_name.data
		print last_name
		full_name = first_name + ' ' + last_name
		db.users.update({'_id' : ObjectId(current_user._id)},
			{	'$set' : {
					'name' : {
						'first' : first_name,
						'last' : last_name,
						'full' : full_name
					}
				}
			})
		flash('Thank you!')
		return redirect(url_for('home'))
	else:
		return render_template('add_name.html', form=form)

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
	prefix = request.args.get('term').lower()
	matches = universities_trie.keys(prefix)
	matches_capitalized = [titleize(school) for school in matches]
	return dumps(matches_capitalized)

