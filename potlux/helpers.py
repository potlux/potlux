from potlux import app, ts
from flask import render_template
from PIL import Image
from werkzeug.security import check_password_hash

import boto.ses
import models
import uuid, os	

def send_verification_email(user):
	token = ts.dumps(user.email, salt=app.config['EMAIL_CONFIRM_KEY'])
	confirm_url = url_for('verify', token=token, _external=True)
	subject = "Congratulations on joining potlux!"
	sender = ""
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

def process_image(file, idea_id):

	# generate new file name
	print "Generating new file name"
	filename = str(uuid.uuid4()) + ".png"

	# change image to better size
	print "Processing image"
	image = Image.open(file)
	print "Opened image:", image
	image.thumbnail((300,300), Image.ANTIALIAS)
	print "Processed image:", image

	#save image as png
	print "saving as png"
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], idea_id)
	print "Saved at:", filepath
	print "searching for existance of directory"
	if not os.path.exists(filepath):
		print "changing permissions of directory"
		os.chmod(app.config['UPLOAD_FOLDER'], 0o777)
		print "making new directory"
		os.mkdir(filepath)
	print "directory made"
	full_path = os.path.join(filepath, filename)
	image.save(full_path, "png")

	relative_path = os.path.join('resources', 'user_images', idea_id, filename)

	return relative_path

def is_allowed(beta_key):
	#check if beta_key is in beta_key database, return True
	
	return True

def get_email(beta_key):
	# returns email associated with beta_key
	return None

