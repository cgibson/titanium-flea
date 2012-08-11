'''
Created on Jul 28, 2012

@author: cgibson
'''

import tiflea.app.settings as s
import datetime, re
import markdown
import tiflea.markdown.ext.mdx_mathjax as mdx_mathjax
import subprocess
import argparse

from sqlite3 import dbapi2 as sqlite3

def createTag(db, name):
    db.execute("replace into tags(name) values(?)", [name])
    
    
def getTagid(db, name):
    cur = db.execute("select id from tags where name==?", [name])
    result = cur.fetchall()
    if not result:
        raise ValueError("No tag exists by name %s" % name)
    return result[0][0]
    
    
def connectTag(db, entryid, name):
    tagid = getTagid(db, name)
    db.execute("insert into tagsXentries(tagid, entryid) values(?, ?)", [tagid, entryid])


def disconnectTag(db, entryid, name):
    tagid = getTagid(db, name)
    db.execute("delete from tagsXentries where tagid==? and entryid==?", [tagid, entryid])


def getTags(db, entryid=None):
    if entryid:
        cur = db.execute("select t.id, t.name from tags t, tagsXentries x where x.entryid==? and t.id==x.tagid", [entryid])
    else:
        cur = db.execute("select id, name from tags")
    
    result = cur.fetchall()
    if not result:
        return []
    else:
        return result
    

def setTags(db, entryid, tags=[]):
    curTags = getTags(db, entryid)
    allTags = getTags(db)
    
    # Disconnect any tags that do not belong anymore
    for tag in curTags:
        if not tag[1] in tags:
            disconnectTag(db, entryid, tag[1])
    
    # Add any tags that don't exist yet
    allTagNames = [tag[1] for tag in allTags]
    for tag in tags:
        if not tag in allTagNames:
            createTag(db, tag)
    
    # Connect any tags that aren't connected
    curTagNames = [tag[1] for tag in curTags]
    for tag in tags:
        if not tag in curTagNames:
            connectTag(db, entryid, tag)
            

def getEntryid(db, urltitle):
    cur = db.execute("select id from entries where urltitle==?", [urltitle])
    result = cur.fetchall()
    if not result:
        raise ValueError("No entry exists with urltitle %s" % urltitle)
    return result[0][0]
    


def publish(title, url_title, text, html, author=s.DEFAULT_AUTHOR, tags=[], created=str(datetime.date.today()), updated=str(datetime.date.today()), preview=False):
    
    db = sqlite3.connect(s.DATABASE)
    
    print "checking for [%s]" % url_title
    cur = db.execute("select id, published from entries where urltitle = '%s'" % url_title)
    result = cur.fetchall()
    if result:
        raw = raw_input("This will replace an existing post of the same title...\nContinue? (y/N)")
        
        # if the existing post is published but we're trying to preview
        if (result[0][1] == True) and preview:
            raise ValueError("Cannot yet preview posts that are already published")
        
        if raw != "y":
            print "Canceling publish."
            return
        else:
            db.execute("""
            update entries set title=?, text=?, html=?, author=?, created=?, modified=?, published=? where urltitle=?
            """,
            [title, text, html, author, created, updated, not preview, url_title])
    else:
        db.execute("""
        insert into entries (title, urltitle, text, html, author, created, modified, published) values(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [title, url_title, text, html, author, created, updated, not preview])
    
    entryid = getEntryid(db, url_title)
    setTags(db, entryid, tags)
    
    db.commit()
    db.close()
    

def url_friendly_text(text):
    text = re.sub("[ ]", "_", text)
    text = re.sub("[\"!',\.~\%\\&\*\$\(\)\?:]", "", text)
    return text.lower()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Publishes posts to the current TiFl blog")
    
    parser.add_argument("title")
    parser.add_argument("post_file", type=argparse.FileType('r'))
    parser.add_argument("-author", default=s.DEFAULT_AUTHOR)
    parser.add_argument("-created", default=str(datetime.date.today()))
    parser.add_argument("-updated", default=str(datetime.date.today()))
    parser.add_argument("-tags", nargs="*", default=[])
    parser.add_argument("-preview", action="store_true", default=False)
    
    opts = parser.parse_args()
    
    title = opts.title
    url_title = url_friendly_text(title)
    text = opts.post_file.read()
    
    # Convert to unicode to avoid silly errors with encoding
    # unicode_content = text.encode('utf8', 'ignore')
    html = markdown.markdown(text, ['codehilite', mdx_mathjax.makeExtension()])
    author = opts.author
    tags = opts.tags
    preview = opts.preview
    created = opts.created
    updated = opts.updated
    
    opts.post_file.close()
    
    publish(title, url_title, text, html, author=author, tags=tags, created=created, updated=updated, preview=preview)
    
    if preview:
        url = "%s/p/%s" % (s.SITE_BASE, url_title)
        subprocess.call(["chromium-browser", url])