from flask import Flask, render_template, request, redirect, g, flash
from flask import session as login_session, make_response, url_for, jsonify

import json
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests

from database.database_setup import User, Catalog, Item, engine, Base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

Base.metadata.bind = engine

# A DBSession() instance establishes all conversations with the database
DBSession = sessionmaker(bind=engine)
session = DBSession()

# client id for google api
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']

# Initialize flask app
app = Flask(__name__)


@auth.verify_password
def verify_password(email, password):
    # Try to see if it's a token first
    # user_id = User.verify_auth_token(username_or_token)
    # if user_id:
    # 	user = session.query(User).filter_by(id = user_id).one()
    # else:
    # 	user =
    # session.query(User).filter_by(username = username_or_token).first()
    # 	if not user or not user.verify_password(password):
    # 		return False
    user = session.query(User).filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


# Route for home URI
@app.route('/')
@app.route('/catalog')
def item_catalog():
    catalogs = session.query(Catalog).all()
    recent = session.query(Catalog.name.label('name'), Item.name.label(
        'sub_name')).join(Item).order_by(Item.id.desc()).limit(7)
    return render_template('home.html', catalogs=catalogs,
                           recent=recent, email=login_session.get('email'))

# Route to display items for catalog selected


@app.route('/catalog/<item>/items')
def items(item):
    catalogs = session.query(Catalog).all()
    values = session.query(Item.name).join(
        Catalog).filter(Catalog.name == item).all()
    print values
    return render_template('specificitem.html', catalogs=catalogs,
                           category=item, items=values,
                           email=login_session.get('email'))

# Route to add item for catalog selected


@app.route('/catalog/new', methods=['GET', 'POST'])
@auth.login_required
def add_item():
    if request.method == 'POST':
        newitem = Item(name=request.form.get('name'),
                       description=request.form.get('description'))
        # check if user has entered category or not
        if not request.form.get('category'):
            # if not, select 1 as default
            catalog_id = 1
            newitem.catalog_id = catalog_id
        else:
            catalog_id = session.query(Catalog.id).filter(
                Catalog.name == request.form.get('category')).first()
            newitem.catalog_id = catalog_id[0]
        session.add(newitem)
        session.commit()
        flash('Added Item %s in %s' %
              (newitem.name, request.form.get('category')))
        return redirect(url_for('item_catalog'))
    else:
        catalogs = session.query(Catalog).all()
        return render_template('newitem.html', catalogs=catalogs,
                               email=login_session.get('email'))

# Route to display item description


@app.route('/catalog/<item>/<sub_item>')
def sub_item(item, sub_item):
    item = session.query(Item.name, Item.description).join(Catalog).filter(
        Catalog.name == item, Item.name == sub_item).first()
    return render_template('showsubitem.html', sub_item=item,
                           email=login_session.get('email'))

# Route to edit items for catalog selected


@app.route('/catalog/<sub_item>/edit', methods=['GET', 'POST'])
@auth.login_required
def edit_item(sub_item):
    eitem = session.query(Item).filter(Item.name == sub_item).first()
    if request.method == 'POST':
        if request.form.get('name'):
            eitem.name = request.form.get('name')
        if request.form.get('description'):
            eitem.description = request.form.get('description')
        if request.form.get('category'):
            catalog_id = session.query(Catalog.id).filter(
                Catalog.name == request.form.get('category')).first()
            eitem.catalog_id = catalog_id[0]
        session.add(eitem)
        session.commit()
        flash('Edited %s' % sub_item)
        return redirect(url_for('item_catalog'))
    else:
        catalogs = session.query(Catalog).all()
        return render_template('edititem.html', catalogs=catalogs,
                               item=eitem, email=login_session.get('email'))

# Route to delete items for catalog selected


@app.route('/catalog/<sub_item>/delete', methods=['GET', 'POST'])
@auth.login_required
def delete_item(sub_item):
    if request.method == 'POST':
        ditem = session.query(Item).filter(Item.name == sub_item).first()
        session.delete(ditem)
        session.commit()
        flash('Successfully Deleted %s' % sub_item)
        return redirect(url_for('item_catalog'))
    else:
        return render_template('deleteitem.html', item=sub_item,
                               email=login_session.get('email'))

# Route for login


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/connect', methods=['POST'])
def connect():
    email = request.form.get('email')
    password = request.form.get('pass')
    user = session.query(User).filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return redirect(url_for('login'))
    login_session['email'] = email
    flash('Successfully Loged In as %s' % email)
    return redirect(url_for('item_catalog'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    id_token = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(id_token)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    login_session['access_token'] = access_token

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user = session.query(User).filter_by(email=data['email']).first()
    if not user:
        user = User(email=data['email'])
        session.add(user)
        session.commit()

    flash('Successfully Loged In as %s' % data['email'])
    output = data['email']
    return output


# Route to display items for catalog selected
@app.route('/logout')
def logout():
    email = login_session.get('email')
    if email is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # access token will be there if user logged in through gplus
    if login_session.get('access_token'):
        # make http request to revoke current logged in user
        token = login_session.get('access_token')
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        if result['status'] == '200':
            del login_session['access_token']
            del login_session['email']
            del login_session['credentials']
            del login_session['gplus_id']
        else:
            response = make_response(json.dumps(
                'Failed to revoke token for given user.', 400))
            response.headers['Content-Type'] = 'application/json'
            return response
    else:
        del login_session['email']
    return redirect(url_for('item_catalog'))


def get_items_category(catalog_id):
    items = session.query(Item).filter_by(catalog_id=catalog_id).all()
    return [i.serialize for i in items]


@app.route('/catalog.json')
def item_catalog_json():
    # have to create a join
    catalogs = session.query(Catalog).all()
    catalog_json = []
    for catalog in catalogs:
        item_json = get_items_category(catalog.id)
        cat_sub_json = catalog.serialize
        if len(item_json):
            cat_sub_json['Item'] = item_json
        catalog_json.append(cat_sub_json)
    return jsonify(Category=catalog_json)


if __name__ == '__main__':
    super_secret_key = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    app.secret_key = super_secret_key
    app.debug = True
    app.run('0.0.0.0', port=5000)


# pep 8 code style
