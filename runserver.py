#############################################################################################################
# We can restructure the application a bit into multiple modules. The only thing we have to remember is 
# the following quick checklist:
# 1) the Flask application object creation has to be in the __init__.py file. That way each module can 
# 	import it safely and the __name__ variable will resolve to the correct package.
#
# 2) all the view functions (the ones with a route() decorator on top) have to be imported in the __init__.py 
# 	file. Not the object itself, but the module it is in. Import the view module after the application 
# 	object is created
##############################################################################################################

from potlux import app
print "Starting server..."
app.run(debug=True)