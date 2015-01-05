# -*- coding: utf-8 -*-
'''Helper utilities and decorators.'''
from flask import flash
from bleach import clean
from bs4 import BeautifulSoup
import re
from blogaggregator.database import db
from blogaggregator.user.models import User
from blogaggregator.user.models import Post
import feedparser


def flash_errors(form, category="warning"):
    '''Flash all errors for a form.'''
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}"
                    .format(getattr(form, field).label.text, error), category)


def check_latest_update(user,new_content):
    '''
    Simple function to update the users latest update if the new content created at
    is newer.
    '''
    if new_content.created_at > user.latest_update:
        user.latest_update = new_content.created_at
        db.session.commit()

 
def summarise_post(content):
    '''
    Summarises and sanitises the post (removes possible javascript CSS).  
    '''
    if len(content)>140:
        summary = clean(content[0:140],strip=True) + " ..."
    else:
        summary = clean(content,strip=True).ljust(144) 
    return summary
    
def clean_feed(content):
    '''
    Cleans up html, removing JS etc and also removes unwanted things like 
    wordpress comment fields
    '''
    
    #define allowed atrtributes, in this case we will additionally allow
    #images
    allowed_attr={
    'a': ['href', 'title'], 
    'abbr': ['title'], 
    'acronym': ['title'],
    'img': ['src','alt'],
    }
    
    allowed_tags=[u'a',
         'abbr',
         'acronym',
         'b',
         'blockquote',
         'code',
         'em',
         'i',
         'li',
         'ol',
         'strong',
         'ul',
         'img']
    
    soup = BeautifulSoup(content)
    [x.extract() for x in soup.findAll('a', href=re.compile('^http://feeds.wordpress'))]
    content = soup.prettify()
    #content = clean(content,strip=True,tags=allowed_tags, attributes=allowed_attr)
    return content

def good_feed(atomfeed):
    '''
    Simple checking function to determine if an atom feed is minimally viable.
    Note, this will return true for all feeds including RSS feeds and feeds that
    are malformed and cannot be passed.  Passing this test does not ensure
    the feed will be usable!
    '''
    print atomfeed
    feed = feedparser.parse(atomfeed)
    
    #check if it is a valid feed
    if feed.bozo != 0:
        print "bad feed"
        return False
    else:
        return True
    
    

def feed_atom(user):
    '''
    Given a user with a valid atom feed, this will read and summarise the feed
    '''
    if good_feed(user.atomfeed):
        entries=feed.entries
        
        #check for the existance of the posts in the database
        for post in entries:
            matching_post = Post.query.filter_by(atomuuid = post.id)
            if matching_post.count() == 0:  #no matching posts
                created_at = datetime.fromtimestamp(mktime(post.published_parsed))
                updated_at = datetime.fromtimestamp(mktime(post.updated_parsed))
                content = post.content[0].value
                summary = summarise_post(content)
                new_post = Post.create(content = clean_feed(content),
                    summary = summary,
                    user_id=user.id,
                    atomuuid=post.id,
                    link=post.link,
                    created_at = created_at)
                #updated user latest update if necessary
                check_latest_update(user,new_post)
                
            
            
        post0=entries[0]
        dt = datetime.fromtimestamp(mktime(post0.updated_parsed))
        
        content=post0.content
        c0=content[0]
        current_post=c0.value
        print "good feed"
        return True
    
