'''
Created on Jul 28, 2012

@author: cgibson
'''

import tifl.web.settings as s
import datetime, re
import markdown
import tifl.md.ext.mdx_mathjax as mdx_mathjax

import argparse

from sqlite3 import dbapi2 as sqlite3


def publish(title, url_title, text, html, author=s.DEFAULT_AUTHOR, tags=[], created=datetime.date.today()):
    
    db = sqlite3.connect(s.DATABASE)
    
    print "checking for [%s]" % url_title
    result = db.execute("select * from entries where urltitle = '%s'" % url_title)
    
    if result.fetchall():
        raw = raw_input("This will replace an existing post of the same title...\nContinue? (y/N)")
        
        if raw != "y":
            print "Canceling publish."
            return
        else:
            db.execute("""
            update entries set title=?, text=?, html=?, author=?, modified=? where urltitle=?
            """,
            [title, text, html, author, str(created), url_title])
    else:
        db.execute("""
        insert into entries (title, urltitle, text, html, author, created, modified) values(?, ?, ?, ?, ?, ?, ?)
        """,
        [title, url_title, text, html, author, str(created), str(created)])
    db.commit()
    db.close()
    

def url_friendly_text(text):
    text = re.sub("[ ]", "_", text)
    text = re.sub("[\"!',\.~\%\\&\*\$\(\)\?]", "", text)
    return text.lower()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Publishes posts to the current TiFl blog")
    
    parser.add_argument("title")
    parser.add_argument("post_file", type=argparse.FileType('r'))
    parser.add_argument("-author", default=s.DEFAULT_AUTHOR)
    parser.add_argument("-tags", nargs="*", default=[])
    
    opts = parser.parse_args()
    
    title = opts.title
    url_title = url_friendly_text(title)
    text = opts.post_file.read()
    html = markdown.markdown(text, ['codehilite', mdx_mathjax.makeExtension()])
    author = opts.author
    tags = opts.tags
    
    opts.post_file.close()
    
    publish(title, url_title, text, html, author, tags)