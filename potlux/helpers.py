from potlux import app
from PIL import Image 

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
