# -*- coding: utf-8 -*-
'''Helper utilities and decorators.'''
from flask import flash
from bleach import clean

def flash_errors(form, category="warning"):
    '''Flash all errors for a form.'''
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}"
                    .format(getattr(form, field).label.text, error), category)

 
def summarise_post(content):
    '''
    Summarises and sanitises the post (removes possible javascript CSS).  
    '''
    if len(content)>140:
        summary = clean(content[0:140]) + " ..."
    else:
        summary = clean(content).ljust(144) 
    return summary
    
