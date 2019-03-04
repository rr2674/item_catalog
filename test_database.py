#!/usr/bin/env python2

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('sqlite:///assignment4.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

categories_tuples = [
 ('Soccer', [('Shinguards', 'blahblah1'), ('Cleats', 'blahblahb2'), ('Ball', 'foofoo')]),
 ('Basketball', [('Headband', 'blahblah3'), ('Shoes', 'blahblah4'), ('Ball', 'blahblah5')]),
 #('Baseball', ['Bat', 'Glove', 'Ball']),
 #('Football', ['Helmet', 'Jersey', 'Shoulder Pads'])
]

for category, items in categories_tuples:
    c = Category(name=category)
    session.add(c)
    session.commit()
    for n, d in items:
        session.add(Item(name=n, description=d, category=c))
        session.commit()

q = session.query(Item).all()
print [i.serialize for i in q]
