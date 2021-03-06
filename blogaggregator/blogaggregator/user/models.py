# -*- coding: utf-8 -*-
import datetime as dt

from flask.ext.login import UserMixin

from blogaggregator.extensions import bcrypt
from blogaggregator.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)


class Role(SurrogatePK, Model):
    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = ReferenceCol('users', nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        return '<Role({name})>'.format(name=self.name)

class User(UserMixin, SurrogatePK, Model):

    __tablename__ = 'users'
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.String(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)
    
    atomfeed = Column(db.String(2000), nullable=True)
    atomposts= Column(db.Integer(), default=0)  
    
    #set last atom date to the UTC time stamp 0, (1970) so we can check for new posts
    latest_atom = Column(db.DateTime, default=dt.datetime.utcfromtimestamp(0),nullable=False)
    
    # Latest update, either post, atom, or comment made on a post of this user
    latest_update = Column(db.DateTime, default=dt.datetime.utcfromtimestamp(0),nullable=False)

    def __init__(self, username, email, password=None, **kwargs):
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        return '<User({username!r})>'.format(username=self.username)
        

class Post(SurrogatePK, Model):
    __tablename__ = 'posts'
    user_id = ReferenceCol('users', nullable=False)
    user = relationship('User', backref='posts')
    
    title = Column(db.String(300), nullable=True, default = "Title")
    content = Column(db.Text(), nullable=False)
    summary = Column(db.Text(), nullable=False)
    
    link = Column(db.String(2000), nullable=True)
    atomuuid = Column(db.String(120), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    edited_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    
    #number of comments
    comment_count = Column(db.Integer(), default=0)  
    
    
class Comment(SurrogatePK, Model):
    __tablename__ = 'comments'
    post_id = ReferenceCol('posts', nullable=False)
    post = relationship('Post', backref='comments')
    
    user_id = ReferenceCol('users', nullable=False)
    user = relationship('User', backref='comments')
    
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    edited_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    
    content = Column(db.Text(), nullable=False)
    
    
    
    

