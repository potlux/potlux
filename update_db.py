from pymongo import MongoClient

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

if __name__ == '__main__':
	change_idea_owners_to_list()
	add_full_name_to_user_model()
