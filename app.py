from flask import Flask, render_template, request
from flask import session as login_session, make_response

import json
import random
import string

# Initialize flask app
app = Flask(__name__)

# Route for home URI
@app.route('/')
@app.route('/catalog')
def itemCatalog():
	return "home"

# Route to display items for catalog selected
@app.route('/catalog/<item>/items')
def items(item):
	return "Selected %s" % item

# Route to display item description
@app.route('/catalog/<item>/<sub_item>')
def sub_item(item, sub_item):
	return "Selected %s, %s" % (item, sub_item)

# Route to edit items for catalog selected
@app.route('/catalog/<sub_item>/edit')
def edit_item(sub_item):
	return "Selected %s" % sub_item

# Route to delete items for catalog selected
@app.route('/catalog/<sub_item>/delete')
def delete_items(sub_item):
	return "Selected %s" % sub_item

# Route for login
@app.route('/login')
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return state

@app.route('/connect', methods = ['POST'])
def connect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

# Route to display items for catalog selected
@app.route('/logout')
def items():
	return "disconnected"

if __name__ == '__main__':
	super_secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	app.secret_key = super_secret_key
	app.debug = True
	app.run('0.0.0.0', port = 5000)
