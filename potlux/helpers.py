from potlux import app
from PIL import Image
from werkzeug.security import check_password_hash

import models
import uuid, os


def process_image(file, idea_id):

	# generate new file name
	filename = str(uuid.uuid4()) + ".png"

	# change image to better size
	image = Image.open(file)
	image.thumbnail((300,300), Image.ANTIALIAS)

	#save image as png
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], idea_id)
	if not os.path.exists(filepath):
		os.mkdir(filepath)
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

