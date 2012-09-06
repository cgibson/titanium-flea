'''
Created on Sep 4, 2012

@author: cgibson
'''

from flask import g


def loadSettings(db=None):
    if not db:
        db = g.db
        
    return db["@blog_settings"]

    