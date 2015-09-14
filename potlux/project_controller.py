from flask import redirect, render_template, url_for, abort, flash
from potlux import db, APP_ROOT, app, ts
from forms import ProjectSubmitForm
from flask.ext.login import current_user
from bson.json_util import loads
from helpers import sanitize_link, process_image, text_or_none, delete_image, send_email
from inflection import titleize
from mongokit import *
import pymongo


class ProjectController:

	def __init__(self, request=None):
		self.request = request

	# Create a project.
	def create(self):
		form = ProjectSubmitForm(self.request.form)
		if form.validate_on_submit():
			name = form.name.data.lower()
			categories = [cat.lower().strip() for cat in form.categories.data.split(",")]
			contact = {'name': current_user.name.full,
					   'email': current_user.email}
			summary = form.summary.data
			university = form.university.data.lower()
			website = sanitize_link(form.website.data.lower())

			new_idea = db.ideas.Idea()
			new_idea.name = name
			new_idea.categories = categories
			new_idea.contacts = [contact]
			new_idea.summary = summary
			new_idea.status = 'active'
			new_idea.university = university
			if website:
				new_idea.resources.websites = [website]

			if current_user.is_authenticated():
				new_idea.owners = [current_user._id]

			new_idea.save()
			return redirect(url_for('show_idea', project_id=str(new_idea._id)))
		else:
			return render_template('submit.html', form=form)

	def delete(self, project_id):
		db.ideas.update({'_id' : ObjectId(project_id)}, {
				'$set' : {
					'status' : 'deleted'
				}
			})
		flash('Project deleted')
		return redirect(url_for('home'))

	def show(self, project_id):
		idea = db.ideas.find_one({"_id" : ObjectId(project_id)})

		# Dictionary of leading questions to be printed if there is no content.
		leading_qs = loads(open(APP_ROOT + '/leading_questions.json').read())
		return render_template('project.html', idea=idea, leading_qs=leading_qs)

	def edit(self, project_id):
		idea = db.ideas.Idea.find_one({"_id" : ObjectId(project_id)})
		if not current_user._id in idea.owners:
			flash("You're not allowed to do that!")
			return app.login_manager.unauthorized()

		if self.request.method == "POST":
			if 'imageUpload' in self.request.files:
				# handle image upload
				filenames = process_image(self.request.files['imageUpload'], project_id)
				db.ideas.update({'_id' : ObjectId(project_id)}, {
						'$addToSet' : {
							'resources.images' : filenames
						}
					})
				if not idea['resources']['project-image']:
					db.ideas.update({'_id' : ObjectId(project_id)}, {
							'$set' : {
								'resources.project-image' : filenames['image_id']
							}
						})
				return redirect(url_for('edit_idea', project_id=project_id))

			else:
				db.ideas.update({'_id' : ObjectId(project_id)},
					{
						'$set': {
							'impact' : text_or_none(self.request.form['impact'].strip()),
							'procedure' : text_or_none(self.request.form['procedure'].strip()),
							'future' : text_or_none(self.request.form['future plans'].strip()),
							'results' : text_or_none(self.request.form['mistakes & lessons learned'].strip()),
							'summary' : text_or_none(self.request.form['summary'].strip())
						}
					})

			return redirect(url_for('show_idea', project_id=project_id))

		# Dictionary of leading questions to be printed if there is no content.
		leading_qs = loads(open(APP_ROOT + '/leading_questions.json').read())

		return render_template('edit_project.html',
			idea=idea, idea_id=str(idea._id), leading_qs=leading_qs)

	def delete_project_image(self, project_id):
		if self.request.method == "DELETE":
			image_id = self.request.args.get('del_image')
			idea = db.ideas.find_one({'_id' : ObjectId(project_id)})

			new_project_image_id = None

			# Set project-image to the id that isn't going to be deleted.
			if image_id == idea['resources']['project-image']:
				# Find first image id that is not the one being deleted.
				for image in idea['resources']['images']:
					if image_id != image['image_id']:
						new_project_image_id = image['image_id']

			# Set new project-image to that image id.
			db.ideas.update({'_id' : ObjectId(project_id)}, {
					'$pull' : {
						'resources.images' : {
							'image_id' : image_id
						}
					},
					'$set' : {
						'resources.project-image' : new_project_image_id
					}
				})

			delete_image(project_id, image_id)
			return "Success!"

	def set_project_image(self, project_id):
		if self.request.method == 'PUT':
			image_id = self.request.args.get('image_id')
			db.ideas.update({'_id' : ObjectId(project_id)}, {
					'$set' : {
						'resources.project-image' : image_id
					}
				})
		return 'Success!'

	def edit_project_tag(self, project_id):
		if self.request.method == "POST":
			new_category = self.request.form['new_cat'].strip().lower()
			if new_category:
				db.ideas.update({'_id' : ObjectId(project_id)},
					{'$addToSet' : {
						'categories' : new_category
					}})
			return redirect(url_for('edit_idea', project_id=project_id))
		if self.request.method == "DELETE":
			delete_cat = self.request.args.get('del_cat')
			db.ideas.update({'_id' : ObjectId(project_id)},
				{'$pull' : {
					'categories' : delete_cat
				}})
			return 'Success!'
		abort(404)

	def edit_project_website(self, project_id):
		if self.request.method == "POST":
			new_website = self.request.form['new_site'].strip().lower()
			if new_website:
				db.ideas.update({'_id' : ObjectId(project_id)},
					{'$addToSet' : {
						'resources.websites' : sanitize_link(new_website)
					}})
			return redirect(url_for('edit_idea', project_id=project_id))
		if self.request.method == "DELETE":
			delete_site = self.request.args.get('del_site')
			db.ideas.update({'_id' : ObjectId(project_id)},
				{'$pull' : {
					'resources.websites' : delete_site
				}})
			return 'Success!'
		abort(404)

	def edit_project_contacts(self, project_id):
		sender = app.config['FROM_EMAIL_ADDRESS']

		if self.request.method == "POST":

			# find user associated with email.
			email = self.request.form['contact_email']
			user = db.users.find_one({'email' : email})

			# generate token and url to send in url to user being added/deleted.
			token_string = email + "&" + project_id
			token = ts.dumps(token_string, salt=app.config['EMAIL_CONFIRM_KEY'])
			confirm_url = url_for('contact_confirm', token=token, _external=True)

			# generate confirmation email body.
			if user and user['name']:
				name = user['name']['first']
			else:
				name = "environmental warrior"

			# generate email fields.
			if current_user.name and current_user.name.first:
				subject = titleize(current_user.name.first) + " wants you to join their project!"
			else:
				subject = current_user.email + " wants you to join their project!"

			recipients = [email]
			text_body = render_template('email/contact_confirm.txt',
				url=confirm_url, name=name)
			html_body = render_template('email/contact_confirm.html',
				url=confirm_url, name=name)

			# send email and redirect user back to edit page.
			send_email(subject, sender, recipients, text_body, html_body)
			flash('An email has been sent to accept your invitation')
			return redirect(url_for('edit_idea', project_id=project_id))

		elif self.request.method == "DELETE":
			print "deleting contact"
			# delete email from list of contacts.
			email = self.request.args.get('del_email')
			print "email:", email
			user = db.users.User.find_one({'email' : email})
			print "user:", user

			# generate token and url to send in url to user being added/deleted.
			token_string = email + "&" + project_id
			token = ts.dumps(token_string, salt=app.config['EMAIL_CONFIRM_KEY'])
			confirm_url = url_for('contact_confirm', token=token, _external=True)
			print "confirm url:", confirm_url

			# Delete user from project.
			if user:
				print "found user, deleting owner and contact from project"
				db.ideas.update({'_id' : ObjectId(project_id)},
					{'$pull' : {
						'contacts' : {
							'email' : user.email
						},
						'owners' : user._id
					}})
			else:
				print "could not find user, deleting contact"
				db.ideas.update({'_id' : ObjectId(project_id)},
					{'$pull' : {
						'contacts' : {
							'email' : email
						}
					}})

			# generate email fields.
			if user and user.name:
				name = user.name.first
			else:
				name = "Environmental warrior"

			subject = "You're being removed from a potlux project!"

			potlux_url = url_for('show_idea', project_id=project_id, _external=True)
			text_body = render_template('email/contact_delete_confirm.txt',
				url=confirm_url,
				name=name,
				potlux_url=potlux_url)
			html_body = render_template('email/contact_delete_confirm.html',
				url=confirm_url,
				name=name,
				potlux_url=potlux_url)
			recipients = [email]
			send_email(subject, sender, recipients, text_body, html_body)
			return 'Success!'

		return abort(404)

	def contact_confirmation(self, project_id):
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
