
# todo: model css from OAuth2.0 project
# todo: https://getbootstrap.com/docs/4.0/layout/grid/#grid-options
# todo: do not let empty items into database...

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc

import random
import string
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
#import httplib2
import requests

from database_setup import Base, Category, Item, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment4.db'
db = SQLAlchemy(app)

def isLoggedIn():
    if 'username' not in login_session:
        return False

    try:
        q = db.session.query(User).filter_by(username=username).one()
    except:
        # TODO: not sure why sqlite gets emptied (tables exist, data is gone)
        print ('==> WARNING: login_session says we are, but db does not record of this user. Forceing logout')
        return redirect(url_for('showCatalog'))

    return True

def getUserInfo(user_id):
    user = db.session.query(User).filter_by(id=user_id).one()
    return user

# TODO: remove me...
@app.route('/admin/login/<username>')
def setUsername(username):
    login_session['username'] = username

    try:
        q = db.session.query(User).filter_by(username=username).one()
    except:
        db.session.add(User(username = username,
                            picture = '',
                            email = '{}.@whatever.com'.format(username)))
        print ('==> added user: {}'.format(username))
        db.session.commit()

        q = db.session.query(User).filter_by(username=username).one()

    login_session['user_id'] = q.id

    return redirect(url_for('showCatalog'))


@app.route('/admin/logout')
def delUsername():
    if 'username' in login_session:
       del login_session['username']
       del login_session['user_id']
    else:
       print ("wierd...no session yet  'add' was there?")

    return redirect(url_for('showCatalog'))


@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = db.session.query(Category).order_by(asc(Category.name)).all()
    items = db.session.query(Item).order_by(desc(Item.create_date)).limit(5).all()

    if 'username' not in login_session:
        if not categories or not items:
            flash('We need data! Please sign in to add data...')

        return render_template('public_catalog.html', categories=categories, items=items)

#    creator = getUserInfo(items.user_id)
#   if  creator.id != login_session['user_id']:

    return render_template('catalog.html', categories=categories, items=items)


@app.route('/catalog/category/new', methods=['GET', 'POST'])
def newCategory():

#    if 'username' not in login_session:
    if not isLoggedIn():
        return redirect('/login')

    if request.method == 'POST':
        q = db.session.query(User).filter_by(username=login_session['username']).one()
        newCategory = Category(name=request.form['name'],
                               user_id=q.id)
        db.session.add(newCategory)
        flash('New category "{}" successfully created'.format(newCategory.name))
        db.session.commit()
        return redirect(url_for('showCatalog'))
    else:
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
            itemtem.description = request.form['description']
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

    return render_template('delete_item.html', item=item)


@app.route('/catalog/<category_name>/items')
def showCategoryItems(category_name):
    categories = db.session.query(Category).order_by(asc(Category.name)).all()

    category = None
    items = None
    try:
        category = db.session.query(Category).filter_by(name=category_name).one()
        items = db.session.query(Item).filter_by(category_id=category.id).all()
    except:
        if category is None:
            flash('Category "{}" does not exist'.format(category_name))
        else:
            flash('No Items for Cagegory "{}" exist'.format(category.name))

        return redirect(url_for('showCatalog'))

    #if 'username' not in login_session:
    if not isLoggedIn():
        return render_template('public_items.html',
                                category_name=category.name,
                                categories=categories,
                                items=items)

    return render_template('items.html',
                            category_name=category.name,
                            categories=categories,
                            items=items)

@app.route('/catalog/<category_name>/items/<item_name>')
def showCategoryItemDescription(category_name, item_name):
    category = None
    items = None
    try:
        category = db.session.query(Category).filter_by(name=category_name).one()
        item = db.session.query(Item).filter_by(name=item_name).one()

    except:
        if category is None:
            flash('Category "{}" does not exist'.format(category_name))
        else:
            flash('Item "{}" for cagegory {} does not exist'.format(item_name, category.name))
        return redirect(url_for('showCatalog'))

    creator = getUserInfo(item.user_id)
    # TODO: replae login_session with  isLoggedIn()...
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_description.html',
                                item=item)

    return render_template('description.html', item=item)



@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/catalog/JSON')
def catalogJSON():
    categories = db.session.query(Category).all()
    print [c.serialize for c in categories]
    return jsonify(categories=[c.serialize for c in categories])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
