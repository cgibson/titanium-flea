'''
Created on Jul 28, 2012

@author: cgibson
'''

import app.settings as s
import datetime
import markdown
import md.ext.mdx_mathjax as mdx_mathjax
import subprocess
import argparse

import couchdb
from post import Post
from settings import BlogSettings

def publish(title, mdtext, html, category, author=s.DEFAULT_AUTHOR, tags=[], timestamp=datetime.datetime.now(), preview=False):


    doc_id = Post.url_friendly_text(title)
    couch = couchdb.Server()
    db = couch["mrvoxel_blog"]
    blog_settings = BlogSettings.getSettings(db)
    
    if not category in blog_settings["categories"]:
        raise ValueError("No such category: %s" % category)
    
    print "checking for [%s]" % doc_id
    
    post = Post.load(db, doc_id)
    
    if post:
        raw = raw_input("This will replace an existing post of the same title...\nContinue? (y/N)")
        
        # if the existing post is published but we're trying to preview
        if (post["published"] == True) and preview:
            raise ValueError("Cannot yet preview posts that are already published")
        
        if raw != "y":
            print "Canceling publish."
            return None
        else:
            post.markdown = mdtext
            post.html = html
            post.author = author
            post.timestamp = timestamp
            post.published = not preview
            post.title = title
            post.tags = tags
            post.category = category
            
            post.store(db)
    else:
        
        post = Post.create(title=title, markdown=mdtext, html=html, category=category, author=author, timestamp=timestamp, published=not preview)
        post.store(db)
        
    return post._id
        

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Publishes posts to the current TiFl blog")
    
    parser.add_argument("title")
    parser.add_argument("post_file", type=argparse.FileType('r'))
    parser.add_argument("category")
    parser.add_argument("-author", default=s.DEFAULT_AUTHOR)
    parser.add_argument("-created", default=datetime.datetime.now())
    parser.add_argument("-tags", nargs="*", default=[])
    parser.add_argument("-preview", action="store_true", default=False)
    
    opts = parser.parse_args()
    
    title = opts.title
    mdtext = opts.post_file.read()
    
    # Convert to unicode to avoid silly errors with encoding
    # unicode_content = text.encode('utf8', 'ignore')
    html = markdown.markdown(mdtext, ['codehilite', mdx_mathjax.makeExtension()])
    author = opts.author
    tags = opts.tags
    preview = opts.preview
    timestamp = opts.created
    category = opts.category
    
    opts.post_file.close()
    
    doc_id = publish(title, mdtext, html, category, author=author, tags=tags, timestamp=timestamp, preview=preview)
    
    if preview and doc_id:
        url = "%s/p/%s" % (s.SITE_BASE, doc_id)
        subprocess.call(["chromium-browser", url])