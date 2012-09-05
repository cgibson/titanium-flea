'''
Created on Sep 4, 2012

@author: cgibson
'''

from couchdb.mapping import ListField, TextField, Document

class BlogSettings(Document):
    categories = ListField( TextField() )
    _id = TextField()
    
    
    @classmethod
    def getSettings(cls, db):
        return cls.load(db, "@blog_general")
    