from potlux import app, ts
from flask import render_template, url_for
from PIL import Image
from werkzeug.security import check_password_hash

import boto.ses
import models
import uuid, os	

def text_or_none(text):
	if text == "None":
		return ""
	else:
		return text

def sanitize_link(link):
	if link and 'http://' in link:
		return link[7:]
	elif link and 'https://' in link:
		return link[8:]
	return link

def send_verification_email(user):
	token = ts.dumps(user.email, salt=app.config['EMAIL_CONFIRM_KEY'])
	confirm_url = url_for('verify', token=token, _external=True)
	subject = "Congratulations on joining Potlux!"
	sender = app.config['FROM_EMAIL_ADDRESS']
	recipients = [user.email]
	text_body = render_template('email/register.txt', url=confirm_url)
	html_body = render_template('email/register.html', url=confirm_url)

	send_email(subject, sender, recipients, text_body, html_body)

def send_email(subject, sender, recipients, text_body, html_body):
	conn = boto.ses.connect_to_region(
		'us-west-2',
		aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
		aws_secret_access_key=app.config['AWS_SECRET_KEY_ACCESS']
	)

	conn.send_email(
		sender,
		subject,
		None,
		recipients,
		text_body=text_body,
		html_body=html_body
	)

##
# Deletes image_id from project_id.
##
def delete_image(idea_id, image_id):
	full_size_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'full_size', idea_id, image_id + '.png')
	thumbnail_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', idea_id, image_id + '.png')
	os.remove(full_size_image_path)
	os.remove(thumbnail_image_path)

def process_image(file, idea_id):

	# generate new file name
	print "Generating new file name"
	image_id = str(uuid.uuid4())
	filename = image_id + ".png"

	# change image to better size
	image = Image.open(file)

	# Create directories for full size image and for thumbnail image.
	print "saving as png"
	full_size_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'full_size', idea_id)
	thumbnail_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', idea_id)
	if not (os.path.exists(full_size_filepath) and os.path.exists(thumbnail_filepath)):
		os.chmod(app.config['UPLOAD_FOLDER'], 0777)
		os.mkdir(full_size_filepath)
		os.mkdir(thumbnail_filepath)

	# Save full size image.
	full_size_path = os.path.join(full_size_filepath, filename)
	image.save(full_size_path, "png")

	# Save thumbnail image.
	image.thumbnail((300,300), Image.ANTIALIAS)
	thumbnail_path = os.path.join(thumbnail_filepath, filename)
	image.save(thumbnail_path, "png")

	thumbnail_relative_path = os.path.join(
		'resources', 'user_images', 'thumbnails', idea_id, filename)
	full_size_relative_path = os.path.join(
		'resources', 'user_images', 'full_size', idea_id, filename)

	return {
		'image_id' : image_id,
		'thumbnail' : thumbnail_relative_path,
		'full_size' : full_size_relative_path
	}

def is_allowed(beta_key):
	#check if beta_key is in beta_key database, return True
	
	return True

def get_email(beta_key):
	# returns email associated with beta_key
	return None

