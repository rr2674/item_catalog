
# todo: model css from OAuth2.0 project

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

import random
import string
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
#import httplib2
import requests


app = Flask(__name__)

engine = create_engine('sqlite:///assignment4.db',connect_args={'check_same_thread':False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/')
def showCatalog():
    restaurants = session.query(Item).order_by(asc(Item.name))
    if 'username' not in login_session:
        return "This page will be the public page."
        #return render_template('publicrestaurants.html', restaurants=restaurants)
    return "This page will allow users to add, edit or delete their own entries."
    #return render_template('restaurants.html', restaurants=restaurants)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
