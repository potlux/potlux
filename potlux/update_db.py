from pymongo import MongoClient
from PIL import Image
import os

def change_idea_owners_to_list():
	client = MongoClient()
	db = client.potlux
	collection = db.ideas
	for doc in collection.find():
		owner = doc['owner']
		contact = doc['contact']
		print owner
		collection.update({'_id' : doc['_id']},
			{'$set': 
				{
					'owners' : [owner],
					'contacts' : [contact]
				}
			})

def add_full_name_to_user_model():
	client = MongoClient()
	db = client.potlux
	collection = db.users
	for doc in collection.find():
		first_name = doc['name.first']
		last_name = doc['name.last']
		full_name = first_name + ' ' + last_name
		doc['full_name'] = full_name

def add_image_ids_to_idea_images():
	client = MongoClient()
	db = client.potlux
	collection = db.ideas
	for doc in collection.find():
		image_count = 0
		for image in doc['resources']['images']:
			image_path = image['thumbnail']
			file_name = os.path.basename(image_path)
			file_name_without_ext = os.path.splitext(file_name)[0]
			collection.update({'_id' : doc['_id']}, {
					'$set' : {
						'resources.images.' + str(image_count) + '.image_id' : file_name_without_ext
					}
				})
			image_count += 1
	print 'Done!'

def compress_existing_images():
	APP_ROOT = os.path.dirname(os.path.abspath(__file__))
	client = MongoClient()
	db = client.potlux
	collection = db.ideas
	for doc in collection.find():
		images = doc['resources']['images']
		for image in images:
			full_size_image_path = os.path.join(APP_ROOT, 'static', image['full_size'])
			print full_size_image_path
			image = Image.open(full_size_image_path)
			image.thumbnail((750, 750))
			image.save(full_size_image_path)

def add_project_image_to_project():
	client = MongoClient()
	db = client.potlux
	collection = db.ideas
	for doc in collection.find():
		db.update({'_id' : doc['_id']}, {
				'$set' : {
					'resources.project-image' : doc['resources']['images'][0]['image_id']
				}
			})

if __name__ == '__main__':
	# change_idea_owners_to_list()
	# add_full_name_to_user_model()
	# add_image_ids_to_idea_images()
	compress_existing_images()
