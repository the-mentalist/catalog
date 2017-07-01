from flask import Flask

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
def items(item, sub_item):
	return "Selected %s, %s" % (item, sub_item)

# Route to edit items for catalog selected
@app.route('/catalog/<sub_item>/edit')
def items(sub_item):
	return "Selected %s" % sub_item

# Route to delete items for catalog selected
@app.route('/catalog/<sub_item>/delete')
def items(sub_item):
	return "Selected %s" % sub_item

# Route for login
@app.route('/login/<provider>')
def items(provider):
	return "Selected %s" % provider

# Route to display items for catalog selected
@app.route('/logout')
def items():
	return "disconnected"
