'''
Created on Sep 1, 2012

@author: cgibson
'''

import re
import datetime

from couchdb.mapping import DateTimeField, ListField, TextField, BooleanField, Document, ViewField

class Post(Document):
    timestamp = DateTimeField()
    tags = ListField( TextField() )
    markdown = TextField()
    html = TextField()
    category = TextField()
    author = TextField()
    published = BooleanField()
    title = TextField()
    _id = TextField()
    #_rev = TextField()
    
    
    @classmethod
    def url_friendly_text(cls, text):
        text = re.sub("[ ]", "_", text)
        text = re.sub("[\"!',\.~\%\\&\*\$\(\)\?:]", "", text)
        return text.lower()
    
    
    @classmethod
    def create(cls, **values):
        
        if not "title" in values:
            raise ValueError("Cannot create post without a title")
        
        values["_id"] = Post.url_friendly_text(values["title"])
        
        if not "timestamp" in values:
            values["timestamp"] = datetime.datetime.now()
        
        
        return cls(**values)
    
    """
    @classmethod
    def _wrap_row(cls, row):
        return map(Document._wrap_row, row['value'])
        
        doc = row.get('doc')
        if doc is not None:
            return cls.wrap(doc)
        data = row['value']
        print row
        data['_id'] = row['id']
        return cls.wrap(data)
    """
    
    def _wrap_post_list(row):
        return map(lambda data: Post.wrap(data), row["value"])
    
    
    def by_tag_reduce(keys, values):
        return values
    
    @ViewField.define('posts', reduce_fun=by_tag_reduce, group=True, wrapper=_wrap_post_list)
    def by_tag(doc):
        if "tags" in doc:
            for tag in doc["tags"]:
                yield tag, doc
    
    
    def by_cat_reduce(keys, values):
        return values
    
    @ViewField.define('posts', reduce_fun=by_cat_reduce, group=True, wrapper=_wrap_post_list)
    def by_cat(doc):
        if "category" in doc:
            yield doc["category"], doc
                
    
    @ViewField.define('posts')
    def by_timestamp(doc):
        if "timestamp" in doc:
            yield doc["timestamp"], doc
            
    @ViewField.define('posts')
    def by_title(doc):
        if "title" in doc:
            yield doc["title"], doc
    