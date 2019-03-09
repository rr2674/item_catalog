#!/usr/bin/env python2

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///assignment4.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#q = session.query(Item).all()
#print [i.serialize for i in q]
#sys.exit()

#q = session.query(Item).order_by(asc(Item.name)).all()
#print [i.serialize for i in q]
#sys.exit()

users = [
('Bob Whatever', '', 'r@comcast.net'),
('Billy Sam', '', 'b@att.com')
]

for name, picture, email  in users:
    session.add(User(username = name, picture = picture, email = email))
    session.commit()

q = session.query(User).filter_by(email='b@att.com').one()
#q = session.query(User).filter_by(email='b@att.com').first()
user1 = q.id

q = session.query(User).filter_by(email='b@att.com').one()
user2 = q.id


categories_tuples = [
 ('Soccer', [('Shinguards', 'blahblah1', user1), ('Cleats', 'blahblahb2', user2), ('Ball', 'foofoo', user1)]),
 ('Basketball', [('Headband', 'blahblah3', user1), ('Shoes', 'blahblah4', user1), ('Ball', 'blahblah5', user2)]),
 #('Baseball', ['Bat', 'Glove', 'Ball']),
 #('Football', ['Helmet', 'Jersey', 'Shoulder Pads'])
]

for category, items in categories_tuples:
    c = Category(name=category)
    session.add(c)
    session.commit()
    q = session.query(Category).filter_by(name=category).one()
    print 'category_id: {}'.format(q.id)
    for n, d, u in items:
        session.add(Item(name=n, description=d, category_id=q.id, user_id=u))
        #session.add(Item(name=n, description=d, user=u))
        #session.add(Item(name=n, description=d, category=q.id, user=u))
        session.commit()

q = session.query(Item).all()
print [i.serialize for i in q]

q = session.query(Item).order_by(asc(Item.name))
print [i.serialize for i in q]
