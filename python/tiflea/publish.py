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

import couchdb


def publish(title, url_title, text, html, author=s.DEFAULT_AUTHOR, tags=[], created=str(datetime.date.today()), updated=str(datetime.date.today()), preview=False):

    couch = couchdb.Server()
    db = couch["mrvoxel_blog"]
    
    print "checking for [%s]" % url_title
    
    results = db.view("blog/by_title")
    
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