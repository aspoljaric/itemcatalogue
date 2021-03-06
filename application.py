from db_connection import *
from flask import Flask, render_template, url_for, request
from flask import redirect, flash, jsonify, abort
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)


# CRUD operations for catalogue
@app.route('/')
@app.route('/catalogue')
def showCatagories():
    with session_scope() as session:
        categories = session.query(Category).all()
        if 'user_id' not in login_session:
            loggedin_user_id = None
        else:
            loggedin_user_id = login_session['user_id']
        return render_template('categories.html', categories=categories,
                               loggedin_user_id=loggedin_user_id)


@app.route('/catalogue/new', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    with session_scope() as session:
        if request.method == 'POST':
            if login_session['state'] != request.form.get('_csrf_token'):
                abort(403)
            newCategory = Category(
                name=request.form['name'], user_id=login_session['user_id'])
            session.add(newCategory)
            flash('New Category "%s" Created.' % request.form['name'])
            return redirect(url_for('showCatagories'))
        else:
            return render_template('new-category.html')


@app.route('/catalogue/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    with session_scope() as session:
        category = session.query(Category).filter_by(id=category_id).one()
        if category.user_id == login_session['user_id']:
            if request.method == 'POST':
                if login_session['state'] != request.form.get('_csrf_token'):
                    abort(403)
                category.name = request.form['name']
                session.add(category)
                flash('Category "%s" Has Been Updated.' % category.name)
                return redirect(url_for('showCatagories'))
            else:
                return render_template('edit-category.html', category=category)
        else:
            return redirect(url_for('showCatagories'))


@app.route('/catalogue/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    with session_scope() as session:
        category = session.query(Category).filter_by(id=category_id).one()
        if category.user_id == login_session['user_id']:
            if request.method == 'POST':
                if login_session['state'] != request.form.get('_csrf_token'):
                    abort(403)
                if category is not None:
                    session.delete(category)
                    flash('Category "%s" Has Been Deleted.' % category.name)
                    return redirect(url_for('showCatagories'))
            else:
                return render_template('delete-category.html',
                                       category=category)
        else:
            return redirect(url_for('showCatagories'))


@app.route('/catalogue/<int:category_id>')
@app.route('/catalogue/<int:category_id>/items')
def showItems(category_id):
    with session_scope() as session:
        if 'user_id' not in login_session:
            loggedin_user_id = None
        else:
            loggedin_user_id = login_session['user_id']
        category = session.query(Category).filter_by(id=category_id).one()
        items = session.query(Item).filter_by(category_id=category_id).all()
        return render_template('items.html', items=items,
                               category_id=category_id,
                               loggedin_user_id=loggedin_user_id,
                               category=category)


@app.route('/catalogue/<int:category_id>/item/new', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    with session_scope() as session:
        category = session.query(Category).filter_by(id=category_id).one()
        if category.user_id == login_session['user_id']:
            if request.method == 'POST':
                if login_session['state'] != request.form.get('_csrf_token'):
                    abort(403)
                newItem = Item(name=request.form['name'],
                               description=request.form['description'],
                               category_id=category_id,
                               user_id=login_session['user_id'])
                session.add(newItem)
                flash('New Item "%s" Created.' % request.form['name'])
                return redirect(url_for('showItems', category_id=category_id))
            else:
                category = session.query(
                    Category).filter_by(id=category_id).one()
                return render_template('new-item.html', category=category)
        else:
            return redirect(url_for('showItems', category_id=category_id))


@app.route('/catalogue/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    with session_scope() as session:
        item = session.query(Item).filter_by(id=item_id).one()
        category = session.query(Category).filter_by(id=category_id).one()
        if item.user_id == login_session['user_id']:
            if request.method == 'POST':
                if login_session['state'] != request.form.get('_csrf_token'):
                    abort(403)
                item.name = request.form['name']
                item.description = request.form['description']
                session.add(item)
                flash('Item "%s" Has Been Updated.' % item.name)
                return redirect(url_for('showItems', category_id=category_id))
            else:
                return render_template('edit-item.html', category=category,
                                       item=item)
        else:
            return redirect(url_for('showItems', category_id=category_id))


@app.route('/catalogue/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    with session_scope() as session:
        item = session.query(Item).filter_by(id=item_id).one()
        if item.user_id == login_session['user_id']:
            if request.method == 'POST':
                if login_session['state'] != request.form.get('_csrf_token'):
                    abort(403)
                session.query(Item).filter_by(id=item_id).delete()
                flash('Item "%s" Has Been Deleted.' % item.name)
                return redirect(url_for('showItems', category_id=category_id))
            else:
                item = session.query(Item).filter_by(id=item_id).one()
                return render_template('delete-item.html', item=item)
        else:
            return redirect(url_for('showItems', category_id=category_id))
# END - CRUD operations for catalogue


# JSON API endpoints
@app.route('/catalogue/JSON')
def catagoriesJSON():
    with session_scope() as session:
        categories = session.query(Category).all()
        return jsonify(Categories=[category.serialize
                                   for category in categories])


@app.route('/catalogue/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
    with session_scope() as session:
        items = session.query(Item).filter_by(category_id=category_id).all()
        return jsonify(Items=[item.serialize for item in items])


@app.route('/catalogue/<int:category_id>/item/<int:item_id>/JSON')
def itemInCategoryJSON(category_id, item_id):
    with session_scope() as session:
        item = session.query(Item).filter_by(
            category_id=category_id).filter_by(id=item_id).one()
        return jsonify(Item=[item.serialize])
# END JSON API endpoints


# User Authentication
CLIENT_ID = json.loads(
    open('client_secret_385075612489-vqap54od740ilifehpt6lokmbtcfe70d'
         '.apps.googleusercontent.com.json',
         'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalogue App"

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    app.jinja_env.globals['csrf_token'] = getToken()
    return render_template('login.html', STATE=state)


@app.route('/googleConnect', methods=['POST'])
def googleConnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secret_385075612489-vqap54od740ilifehpt6lokmbtcfe70d'
            '.apps.googleusercontent.com.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['credentials'] = credentials.access_token
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    flash("You have successfully been logged in.")
    output = 'OK'
    return output


@app.route('/googleDisconnect')
def googleDisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect based on provider


@app.route('/signout')
def signout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            googleDisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatagories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatagories'))


def getToken():
    if login_session['state']:
        return login_session['state']

# User Helper Functions


def createUser(login_session):
    with session_scope() as session:
        newUser = User(name=login_session['username'], email=login_session[
                       'email'], picture=login_session['picture'])
        session.add(newUser)
        user = session.query(User).filter_by(
            email=login_session['email']).one()
        return user.id


def getUserInfo(user_id):
    with session_scope() as session:
        user = session.query(User).filter_by(id=user_id).one()
        return user


def getUserID(email):
    try:
        with session_scope() as session:
            user = session.query(User).filter_by(email=email).one()
            return user.id
    except:
        return None

# END User Authentication

if __name__ == '__main__':
    app.secret_key = '17763f3d2dd9f6762cd967ee53efdb82'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
