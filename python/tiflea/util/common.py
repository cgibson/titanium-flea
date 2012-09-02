'''
Created on Aug 3, 2012

@author: cgibson
'''
from flask import g
import flask
import iso8601

def helloWorld():
    return "Hello, World!"

def getRecentEntries():
    results = g.db.view("blog/by_date")
    #cur = g.db.execute('select id, title, urltitle, html, author, created, published from entries order by id desc')
    entries = []
    for row in results:
        data = row.value
    #for row in cur.fetchall():
        # skip if not published
        if not data["published"]:
            continue
        
        entry = dict(title=data["title"], html=data["html"], author=data["author"], created=data["timestamp"], tags=data["tags"])
        
        # Create a datetime object from our timestamp.
        d = iso8601.parse_date( entry["created"] )
        
        months = ["jan", "feb", "mar", "apr",
                  "may", "jun", "jul", "aug", 
                  "sep", "oct", "nov", "dec"]
        
        entry["created_month"] = months[d.month - 1]
        entry["created_day"] = d.day
        
        # Build entry url
        url = "%s/p/%s" % (flask.current_app.config["SITE_BASE"], data["_id"])
        entry["url"] = url
        
        entries.append(entry)
        
    return entries