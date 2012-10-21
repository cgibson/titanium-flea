'''
Created on Jul 28, 2012

@author: cgibson
'''

import datetime
import markdown
import md.ext.mdx_mathjax as mdx_mathjax
import subprocess
import argparse

import couchdb
from post import Post
import settings

def publish(post_meta):


    doc_id = Post.url_friendly_text(post_meta["title"])
    
    # Open the database
    couch = couchdb.Server()
    db = couch["mrvoxel_blog"]
    
    # Load the database settings
    blog_settings = settings.loadSettings(db)
    
    # Check to see if we have a valid category
    if not post_meta["category"] in blog_settings["blog_categories"]:
        raise ValueError("No such category: %s" % post_meta["category"])
    
    print "checking for [%s]" % doc_id
    
    # Load the post (if it exists in our database)
    post = Post.load(db, doc_id)
    
    # If it exists, warn the user
    if post:
        raw = raw_input("This will replace an existing post of the same title...\nContinue? (y/N)")
        
        # if the existing post is published but we're trying to preview
        if (post["published"] == False) and post_meta["published"]:
            raise ValueError("Cannot yet preview posts that are already published")
        
        if raw != "y":
            print "Canceling publish."
            return None
        else:
            for k, v in post_meta.iteritems():
                if k not in ["published", "title"]:
                    print k
                    post[k] = v
            
            print post
            
            """
            post.markdown = mdtext
            post.html = html
            post.author = author
            post.timestamp = timestamp
            post.published = not preview
            post.title = title
            post.tags = tags
            post.category = category
            """
            
            post.store(db)
    else:
        
        post = Post.create(**post_meta)
        print post["_id"]
        post.store(db)
        print post["_id"]
    return post["_id"]
        

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Publishes posts to the current TiFl blog")
    
    parser.add_argument("post_file", type=argparse.FileType('r'))
    parser.add_argument("-title", default=None)
    parser.add_argument("-category", default=None)
    parser.add_argument("-author", default=None)
    parser.add_argument("-date", default=None)
    parser.add_argument("-tags", nargs="*", default=None)
    parser.add_argument("-preview", action="store_true", default=False)
    
    # Parse the arguments
    opts = parser.parse_args()
    
    # Create the post argument dictionary
    post_meta = {}
    
    # Create the markdown file
    md = markdown.Markdown(extensions=['codehilite','meta', mdx_mathjax.makeExtension()])
    
    # Load the markdown text and create the html from it
    post_meta["markdown"] = opts.post_file.read()
    opts.post_file.close()
    post_meta["html"] = md.convert(post_meta["markdown"])
    
    print md.Meta
    # Load file-based metadata
    for k, v in md.Meta.iteritems():
        if k in ["markdown", "html"]:
            continue
        
        # Necessary conversions for arrays
        if k == "tags":
            tags = []
            for line in v:
                tags += line.split(" ")
            v = tags
        else:
            v = v[0]
        
        # Other random conversions
        if k == "date":
            k = "timestamp"
            v = datetime.datetime.strptime(v, "%m/%d/%Y")
        
        # Save the data
        post_meta[k] = v
    
    # Now overwrite any metadata if explicitely listed in the arguments
    if opts.title:
        post_meta["title"] = opts.title
    
    if opts.author:
        post_meta["author"] = opts.author
    
    if opts.tags:
        post_meta["tags"] = opts.tags
    
    if opts.date:
        post_meta["timestamp"] = datetime.datetime.strptime(opts.date, "%m/%d/%Y")
    
    if opts.category:
        post_meta["category"] = opts.category
    
    post_meta["published"] = not opts.preview
    
    doc_id = publish(post_meta)
    
    #if preview and doc_id:
    #    url = "%s/p/%s" % (s.SITE_BASE, doc_id)
    #    subprocess.call(["chromium-browser", url])