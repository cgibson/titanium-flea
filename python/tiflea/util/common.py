'''
Created on Aug 3, 2012

@author: cgibson
'''
from flask import g
import flask

def helloWorld():
    return "Hello, World!"

def getRecentEntries():
    cur = g.db.execute('select id, title, urltitle, html, author, created, published from entries order by id desc')
    entries = []
    for row in cur.fetchall():
        # skip if not published
        if not row[6]:
            continue
        
        entry = dict(title=row[1], html=row[3], author=row[4], created=row[5])
        
        months = ["jan", "feb", "mar", "apr",
                  "may", "jun", "jul", "aug", 
                  "sep", "oct", "nov", "dec"]
        
        date_tokens = entry["created"].split("-")
        entry["created_month"] = months[int(date_tokens[1]) - 1]
        entry["created_day"] = date_tokens[2]
        
        # Build entry url
        url = "%s/p/%s" % (flask.current_app.config["SITE_BASE"], row[2])
        entry["url"] = url
        
        # Build tag list
        cur = g.db.execute('select t.name from tags t, tagsXentries x where x.entryid==? and x.tagid==t.id',[row[0]])
        entry["tags"] = [tag[0] for tag in cur.fetchall()]
        entries.append(entry)
        
    return entries