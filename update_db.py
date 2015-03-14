from pymongo import MongoClient

def change_idea_owners_to_list():
	client = MongoClient()
	db = client.potlux
	collection = db.ideas
	for doc in collection.find():
		owner = doc['owner']
		print owner
		collection.update({'_id' : doc['_id']},
			{'$set': 
				{
					'owners' : [owner]
				}
			})


if __name__ == '__main__':
	change_idea_owners_to_list()
