# -*- coding: utf-8 -*-
'''Helper utilities and decorators.'''
from flask import flash
from bleach import clean
from bs4 import BeautifulSoup
import re
from blogaggregator.database import db


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
    
