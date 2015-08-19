from flask import redirect, render_template, url_for
from potlux import db
from forms import ProjectSubmitForm
from flask.ext.login import current_user
from helpers import sanitize_link
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
			new_idea.university = university
			if website:
				new_idea.resources.websites = [website]

			if current_user.is_authenticated():
				new_idea.owners = [current_user._id]

			new_idea.save()
			return redirect(url_for('show_idea', project_id=str(new_idea._id)))
		else:
			print form.errors
			return render_template('submit.html', form=form)

	def show(self, project_id):
		idea = db.ideas.find_one({"_id" : ObjectId(project_id)})

		# Dictionary of leading questions to be printed if there is no content.
		leading_qs = loads(open(APP_ROOT + '/leading_questions.json').read())
		return render_template('project.html', idea=idea, leading_qs=leading_qs)
