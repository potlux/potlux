from potlux import app

@app.route('/')
def home():
	return 'Welcome to potlux!'