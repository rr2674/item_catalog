# todo: rate limit...
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, g
from flask import session as login_session
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc

import random
import string
import json

from google.oauth2 import id_token
from google.auth.transport import requests as g_requests
import httplib2
import requests

from database_setup import Base, Category, Item, User


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment4.db'
with app.app_context():
    print('=!' * 40)

db = SQLAlchemy(app)


@app.before_request
def cleanup():
    """
    https://stackoverflow.com/questions/11783025/is-there-an-easy-way-to-make-sessions-timeout-in-flask
    """
    if 'username' in login_session and 'user_id' in login_session:
        if getUserId(login_session['user_id']) is None:
            print ('==> INFO: clean up session for stale browser conection')
            del login_session['username']
            del login_session['user_id']


def get_google_client_id():
    return json.loads(
      open('client_secret_google.json',
           'r').read())['web']['client_id']


def isLoggedIn():
    if 'username' not in login_session and 'user_id' not in login_session:
        return False

    # TODO: this block of code should get deleted...
    if getUserId(login_session['user_id']) is None:
        print ('==> CLEANUP????')
        return redirect(url_for('showCatalog'))

    return True


def getUserId(user_id):
    try:
        user = db.session.query(User).filter_by(id=user_id).one()
    except:
        return None

    return user


def getUserIdByEmail(email):
    try:
        user = db.session.query(User).filter_by(email=email).one()
    except:
        return None

    return user.id


def createUser(login_session):
    db.session.add(User(username = login_session['username'],
                        picture = login_session['picture'],
                        email = login_session['email']))
    db.session.commit()

    return getUserIdByEmail(login_session['email'])


@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = db.session.query(Category).order_by(asc(Category.name)).all()

    if not isLoggedIn():
        items = db.session.query(Item).order_by(desc(Item.create_date)).all()
        if not categories or not items:
            flash('We need data! Please sign in to add data...')


        return render_template('public_catalog.html',
                               categories=categories,
                               items=items)

    items = db.session.query(Item).filter_by(user_id=login_session['user_id']).order_by(desc(Item.create_date)).all()
    return render_template('catalog.html',
                           categories=categories,
                           items=items,
                           provider=login_session['provider'])


@app.route('/catalog/category/new', methods=['GET', 'POST'])
def newCategory():
    if not isLoggedIn():
        return redirect('/login')

    if request.method == 'POST':
        q = db.session.query(User).filter_by(username=login_session['username']).one()
        newCategory = Category(name=request.form['name'], user_id=q.id)
        db.session.add(newCategory)
        flash('New category "{}" successfully created'.format(newCategory.name))
        db.session.commit()
        return redirect(url_for('showCatalog'))

    return render_template('new_catalog.html', action='New Item')


@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
    if not isLoggedIn():
        return redirect('/login')

    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category_id'],
                       user_id=login_session['user_id'])
        db.session.add(newItem)
        flash('New item "{}" successfully created'.format(newItem.name))
        db.session.commit()
        return redirect(url_for('showCatalog'))

    categories = db.session.query(Category).order_by(asc(Category.name)).all()
    return render_template('add_edit_item.html', action='New Item', categories=categories)


@app.route('/catalog/<category_name>/items/<item_name>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if not isLoggedIn():
        return redirect('/login')

    item = db.session.query(Item).filter_by(name=item_name).one()
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category_id']:
            item.category_id = request.form['category_id']
        db.session.add(item)
        db.session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showCatalog'))

    categories = db.session.query(Category).order_by(asc(Category.name)).all()
    return render_template('add_edit_item.html', action='Edit Item', item=item, categories=categories)


@app.route('/catalog/<category_name>/items/<item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    if not isLoggedIn():
        return redirect('/login')

    item = db.session.query(Item).filter_by(name=item_name).one()

    if request.method == 'POST':
        db.session.delete(item)
        db.session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCatalog'))

    return render_template('delete_item.html', item=item, action='Edit Item' )


@app.route('/catalog/<category_name>/items')
def showCategoryItems(category_name):
    categories = db.session.query(Category).order_by(asc(Category.name)).all()

    category = None
    try:
        category = db.session.query(Category).filter_by(name=category_name).one()
    except:
        if category is None:
            flash('Category "{}" does not exist'.format(category_name))

        return redirect(url_for('showCatalog'))

    if not isLoggedIn():
        items = db.session.query(Item).filter_by(category_id=category.id).all()
        return render_template('public_items.html',
                                category_name=category.name,
                                categories=categories,
                                items=items)

    items = db.session.query(Item).filter_by(category_id=category.id, user_id=login_session['user_id']).all()
    if not items:
        flash('You do not yet own any items in category {}'.format(category.name))
    return render_template('items.html',
                            category_name=category.name,
                            categories=categories,
                            items=items,
                            provider=login_session['provider'])


@app.route('/catalog/<category_name>/items/<item_name>')
def showCategoryItemDescription(category_name, item_name):
    category = None
    try:
        category = db.session.query(Category).filter_by(name=category_name).one()
        item = db.session.query(Item).filter_by(name=item_name).one()
    except:
        if category is None:
            flash('Category "{}" does not exist'.format(category_name))
        else:
            flash('Item "{}" for cagegory {} does not exist'.format(item_name, category.name))
        return redirect(url_for('showCatalog'))

    creator = getUserId(item.user_id)
    if not isLoggedIn() or creator.id != login_session['user_id']:
            return render_template('public_description.html', item=item)

    return render_template('description.html', item=item, provider=login_session['provider'])


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, google_client_id=get_google_client_id())


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''
    The example provided in OATH2 lessons stopped working for me... it did work
    few weeks back, I think it may be realted to the shutdown of google+
    I started @ https://developers.google.com/identity/sign-in/web/quick-migration-guide
    I then followed the instructions @ https://developers.google.com/identity/sign-in/web/backend-auth
    '''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    token = request.data

    try:
        idinfo = id_token.verify_oauth2_token(token, g_requests.Request(), get_google_client_id())
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            response = make_response(json.dumps('Wrong issuer.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
    except ValueError as e:
        response = make_response(json.dumps('oauth_token error: {}'.format(e)), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['username'] = idinfo['name']
    login_session['email'] = idinfo['email']
    login_session['picture'] = idinfo['picture']
    login_session['provider'] = 'google'

    user_id = getUserIdByEmail(idinfo['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    #flash('Successfully logged in...')
    response = make_response(json.dumps({ 'name': login_session['username']}), 200)
    response.headers['Content-Type'] = 'application/json'

    return response

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    if 'email' in data:
        login_session['email'] = data["email"]
    else:
        #email not required when you create an id with phone number...
        login_session['email'] = '{}@no_fb_email_avail'.format(data['name'])
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    user_id = getUserIdByEmail(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    response = make_response(json.dumps({ 'name': login_session['username']}), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/disconnect')
def disconnect():
    """
     Revoke a current user's token and reset their login_session
    """
    provider = login_session.get('provider')
    if provider is None:
        flash('You are not logged in...')
        redirect(url_for('showCatalog'))


    flash('{}, you are now logged out from {}'.format(login_session['username'], login_session['provider']))
    if provider == 'google':
        #my research suggests id_token is all you need...
        #  g-signin2 with googleuser.getAuthResponse appears to not expose auth_token
        #  as a result, I not yet found how to 'revoke' the auth token - or equivellent
        #  when all I have is id_token...
        #  note: I think i should be using sub from id_token instead of email
        pass
    else:
        facebook_id = login_session['facebook_id']
        # The access token must me included to successfully logout
        access_token = login_session['access_token']
        url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
        print('FB delete acess token result {}'.format(result))
        del login_session['facebook_id']
        del login_session['access_token']

    del login_session['picture']
    del login_session['username']
    del login_session['email']
    del login_session['user_id']
    del login_session['provider']

    return redirect(url_for('showCatalog'))


@app.route('/catalog/JSON')
def catalogJSON():
    categories = db.session.query(Category).all()
    #print [c.serialize for c in categories]
    return jsonify(categories=[c.serialize for c in categories])


def load_category_table():
    """
    Pre-populate category table with the following list.
    """
    categories = [ 'Soccer',
                   'Basketball',
                   'Baseball',
                   'Frisbee',
                   'Snowboarding',
                   'Rock Climbing',
                   'Football',
                   'Skating',
                   'Hockey'
                  ]
    for category in categories:
        db.session.add(Category(name=category))
        db.session.commit()


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    #app.secret_key = "'\x7f\x90TW3#\xe8X\xcc\xd9VNb\xba\x91"
    app.debug = True
    load_category_table()
    app.run(host='0.0.0.0', port=8000)
