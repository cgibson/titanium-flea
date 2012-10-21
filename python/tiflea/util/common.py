'''
Created on Aug 3, 2012

@author: cgibson
'''
from flask import g
import flask
import iso8601
from tiflea.post import Post

def helloWorld():
    return "Hello, World!"

def getRecentEntries():
    posts = Post.by_date(g.db, limit=5, descending=True)
    #results = g.db.view("blog/by_title")
    outPosts = []
    for post in posts:
    #for row in cur.fetchall():
        # skip if not published
        if not post["published"]:
            continue
        
        # Create a datetime object from our timestamp.
        d = iso8601.parse_date( post["date"] )
        
        months = ["jan", "feb", "mar", "apr",
                  "may", "jun", "jul", "aug", 
                  "sep", "oct", "nov", "dec"]
        
        post["created_month"] = months[d.month - 1]
        post["created_day"] = d.day
        
        # Build entry url
        url = "%s/p/%s" % (flask.current_app.config["SITE_BASE"], post["_id"])
        post["url"] = url
        
        outPosts.append(post)
        
    return outPosts