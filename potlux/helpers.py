from potlux import app
from PIL import Image
from werkzeug.security import check_password_hash

import models
import uuid, os


def process_image(file):

	# generate new file name
	filename = str(uuid.uuid4()) + ".png"

	# change image to better size
	image = Image.open(file)
	image.thumbnail((300,300), Image.ANTIALIAS)

	#save image as png
	image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename), "png")

	return filename

def is_allowed(beta_key):
	#check if beta_key is in beta_key database, return True
	
	return True

def get_email(beta_key):
	# returns email associated with beta_key
	return None

