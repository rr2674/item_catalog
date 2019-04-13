#!/usr/bin/env python2

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

#from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


class User(Base):
    #changed name from user to my_users...
    # as users is a postgresql reserve word
    __tablename__ = 'my_users'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)

    def generate_auth_token(self, expiration=600):
    	s = Serializer(secret_key, expires_in = expiration)
    	return s.dumps({'id': self.id })

    @staticmethod
    def verify_auth_token(token):
    	s = Serializer(secret_key)
    	try:
    		data = s.loads(token)
    	except SignatureExpired:
    		#Valid Token, but expired
    		return None
    	except BadSignature:
    		#Invalid Token
    		return None
    	user_id = data['id']
    	return user_id


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('my_users.id'))
    user = relationship('User')
    items = relationship('Item', back_populates='category')

    @property
    def serialize(self):
        items = []
        for item in self.items:
            items.append(
                {
                    'name': item.name,
                    'id': item.id,
                    'description': item.description,
                    'created': item.create_date.strftime('%Y-%m-%d %H:%M'),
                    'category_id': item.category_id
                }
            )
        return {
            'id': self.id,
            'name': self.name,
            'items': items
        }


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    create_date = Column(DateTime, default=datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship('Category')
    user_id = Column(Integer, ForeignKey('my_users.id'))
    user = relationship('User')


# serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'create_date': self.create_date.strftime('%Y%m%d'),
            'category': self.category.name,
            'user': self.user.username
        }


def load_category_table(session):
    """
    Pre-populate category table with the following list.
    """
    categories = ['Soccer',
                  'Basketball',
                  'Baseball',
                  'Frisbee',
                  'Snowboarding',
                  'Rock Climbing',
                  'Football',
                  'Skating',
                  'Hockey']

    for category in categories:
        session.add(Category(name=category))
        session.commit()


if __name__ == "__main__":
    engine = create_engine('postgresql://catalog:whatever@localhost:5432/catalog')

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    load_category_table(session)
