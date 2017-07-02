from flask import Flask, render_template, request, redirect
from flask import session as login_session, make_response, url_for

import json
import random
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database_setup import User, Catalog, Item, engine, Base

Base.metadata.bind = engine

# A DBSession() instance establishes all conversations with the database
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Initialize flask app
app = Flask(__name__)

# Route for home URI
@app.route('/')
@app.route('/catalog')
def item_catalog():
	catalogs = session.query(Catalog).all()
	recent = session.query(Catalog.name.label('name'), Item.name.label('sub_name')).join(Item).order_by(Item.id.desc()).limit(7)
	return render_template('home.html', catalogs=catalogs, recent=recent)

# Route to display items for catalog selected
@app.route('/catalog/<item>/items')
def items(item):
	catalogs = session.query(Catalog).all()
	values = session.query(Item.name).join(Catalog).filter(Catalog.name == item).all()
	print values
	return render_template('specificitem.html', catalogs=catalogs, category=item, items=values)

# Route to add item for catalog selected
@app.route('/catalog/new', methods=['GET', 'POST'])
def add_item():
	if request.method == 'POST':
		newitem = Item(name=request.form.get('name'),description=request.form.get('description'))
		# check if user has entered category or not
		if not request.form.get('category'):
			# if not, select 1 as default
			catalog_id = 1
			newitem.catalog_id = catalog_id
		else:
			catalog_id = session.query(Catalog.id).filter(Catalog.name == request.form.get('category')).first()
			newitem.catalog_id = catalog_id
		session.add(newitem)
		session.commit()
		return redirect(url_for('item_catalog'))
	else:
		catalogs = session.query(Catalog).all()
		return render_template('newitem.html', catalogs=catalogs)

# Route to display item description
@app.route('/catalog/<item>/<sub_item>')
def sub_item(item, sub_item):
	item = session.query(Item.name, Item.description).join(Catalog).filter(Catalog.name==item, Item.name==sub_item).first()
	return render_template('showsubitem.html', sub_item=item)

# Route to edit items for catalog selected
@app.route('/catalog/<sub_item>/edit', methods=['GET', 'POST'])
def edit_item(sub_item):
	eitem = session.query(Item).filter(Item.name == sub_item).first()
	if request.method == 'POST':
		if request.form.get('name'):
			eitem.name = request.form.get('name')
		if request.form.get('description'):
			eitem.description = request.form.get('description')
		if request.form.get('category'):
			catalog_id = session.query(Catalog.id).filter(Catalog.name == request.form.get('category')).first()
			eitem.catalog_id = catalog_id[0]
		session.add(eitem)
		session.commit()
		return redirect(url_for('item_catalog'))
	else:
		catalogs = session.query(Catalog).all()
		return render_template('edititem.html', catalogs=catalogs, item=eitem)

# Route to delete items for catalog selected
@app.route('/catalog/<sub_item>/delete', methods=['GET', 'POST'])
def delete_item(sub_item):
	if request.method == 'POST':
		ditem = session.query(Item).filter(Item.name==sub_item).first()
		session.delete(ditem)
		session.commit()
		return redirect(url_for('item_catalog'))
	else:
		return render_template('deleteitem.html', item=sub_item)

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
def logout():
	return "disconnected"

if __name__ == '__main__':
	super_secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	app.secret_key = super_secret_key
	app.debug = True
	app.run('0.0.0.0', port = 5000)
