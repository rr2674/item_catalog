
# todo: model css from OAuth2.0 project
# todo: https://getbootstrap.com/docs/4.0/layout/grid/#grid-options

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc

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

#engine = create_engine('sqlite:///assignment4.db',connect_args={'check_same_thread':False})

@app.route('/')
@app.route('/catalog')
def showCatalog():
    # TODO: the queries should be moved under if statement...
    categories = db.session.query(Category).order_by(asc(Category.name)).all()
    items = db.session.query(Item).order_by(asc(Item.create_date)).limit(5).all()
    if 'username' not in login_session:
        if not categories or not items:
            flash('We need data! Please sign in to add data...')

        return render_template('public_catalog.html', categories=categories, items=items)

    return "This page will allow users to add, edit or delete their own entries."
    #return render_template('restaurants.html', restaurants=restaurants)

# TODO: change to use category.name vs id...
@app.route('/catalog/<int:category_id>/items')
def showCategoryItems(category_id):
    categories = db.session.query(Category).order_by(asc(Category.name)).all()
    if 'username' not in login_session:
        category = None
        items = None
        try:
            category = db.session.query(Category).filter_by(id=category_id).one()
            items = db.session.query(Item).filter_by(category_id=category_id).all()
        except:
            if category is None:
                flash('Category does not exist')
            else:
                flash('No Items for Cagegory {} exist'.format(category.name))

            return redirect(url_for('showCatalog'))

        return render_template('public_items.html',
                                category_name=category.name,
                                categories=categories,
                                items=items)

    return "This page will allow users to add, edit or delete their own items to a category."
    #return render_template('restaurants.html', restaurants=restaurants)

@app.route('/catalog/<int:category_id>/items/<int:item_id>')
def showCategoryItemDescription(category_id, item_id):
    if 'username' not in login_session:
        category = None
        items = None
        try:
            category = db.session.query(Category).filter_by(id=category_id).one()
            item = db.session.query(Item).filter_by(id=item_id).one()
        except:
            if category is None:
                flash('Category does not exist')
            else:
                flash('No Items for Cagegory {} exist'.format(category.name))

            return redirect(url_for('showCatalog'))

        return render_template('public_description.html',
                                item=item)

    return "This page will allow users to add, edit or delete their own items to a category."



@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
