from __future__ import with_statement

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from tripy.utils.path import Path
import settings as s
import os
from contextlib import closing
import sys
from werkzeug.contrib.atom import AtomFeed
import datetime, iso8601
from tiflea import util

from tiflea.post import Post
import couchdb
#from sqlite3 import dbapi2 as sqlite3

_app = Flask(__name__, template_folder=s.TEMPLATE_DIR, static_folder=s.STATIC_DIR)
_app.config.from_object(s)

# Load override configuration values into flask config
#
override = Path("config.py")
root = Path(_app.root_path)
if override.exists():
    _app.config.from_pyfile(str(override.abspath()))


def connect_db(db_name):
    #return sqlite3.connect(_app.config['DATABASE'])
    couch = couchdb.Server()
    couch.resource.credentials = ("testuser","spacejanitor")
    return couch[db_name]


def init_db():
    """Creates the database tables."""
    """
    with closing(connect_db()) as db:
        with _app.open_resource('../../scripts/schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
    """
    pass


@_app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db("mrvoxel_blog")


@_app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    #if hasattr(g, 'db'):
    #    g.db.close()


@_app.route('/')
def show_entries():
    
    #cur = g.db.execute('select id, title, urltitle, html, author, created, published from entries order by id desc')
    Post.by_title.sync(g.db)
    Post.by_tag.sync(g.db)
    posts = Post.by_title(g.db)
    #results = g.db.view("blog/by_title")
    outPosts = []
    print posts.rows
    for post in posts:
    #for row in cur.fetchall():
        # skip if not published
        print post
        if not post["published"]:
            continue
        
        # Create a datetime object from our timestamp.
        d = iso8601.parse_date( post["timestamp"] )
        
        months = ["jan", "feb", "mar", "apr",
                  "may", "jun", "jul", "aug", 
                  "sep", "oct", "nov", "dec"]
        
        post["created_month"] = months[d.month - 1]
        post["created_day"] = d.day
        
        # Build entry url
        url = "%s/p/%s" % (_app.config["SITE_BASE"], post["_id"])
        post["url"] = url
        
        outPosts.append(post)

    return render_template('show_entries.html', entries=outPosts, util=util)

@_app.route('/feed')
def feed():

    feed = AtomFeed('Mr.Voxel Articles',
                    feed_url=request.url, url=request.url_root)

    Post.by_title.sync(g.db)
    posts = Post.by_title(g.db)

    for post in posts:
    #for row in cur.fetchall():
        # skip if not published
        print post
        if not post["published"]:
            continue

        # Build entry url
        url = "%s/p/%s" % (_app.config["SITE_BASE"], post["_id"])
        
        feed.add(post.title, 
                 unicode(post.html), 
                 content_type="html",
                 author=post.author,
                 url=url,
                 updated=post.timestamp,
                 published=post.timestamp
                 )

    return feed.get_response()


@_app.route('/p/<post_id>')
def single_entry(post_id):

    #cur = g.db.execute('select id, title, urltitle, html, author, created, published from entries where urltitle==?',[urltitle])
    #result = cur.fetchone()
    post = Post.load(g.db, post_id)
    
    # Create a datetime object from our timestamp.
    d = iso8601.parse_date( post["timestamp"] )
    
    months = ["jan", "feb", "mar", "apr",
              "may", "jun", "jul", "aug", 
              "sep", "oct", "nov", "dec"]
    
    post["created_month"] = months[d.month - 1]
    post["created_day"] = d.day
    
    # Build entry url
    url = "%s/p/%s" % (_app.config["SITE_BASE"], post["_id"])
    post["url"] = url
        
    return render_template('single_entry.html', entry=post, util=util)


@_app.route('/t/<tagname>')
def tag_entries(tagname):
    Post.by_tag.sync(g.db)
    
    # We're sure we're only getting one value here
    results = Post.by_tag(g.db, key=tagname)
    outPosts = []
    
    for posts in results:
        
        # Now that we finally have all of the post data, iterate through the list
        for post in posts:

            # skip if not published
            if not post["published"]:
                continue
            
            # Create a datetime object from our timestamp.
            d = iso8601.parse_date( post["timestamp"] )
            
            months = ["jan", "feb", "mar", "apr",
                      "may", "jun", "jul", "aug", 
                      "sep", "oct", "nov", "dec"]
            
            post["created_month"] = months[d.month - 1]
            post["created_day"] = d.day
            
            # Build entry url
            url = "%s/p/%s" % (_app.config["SITE_BASE"], post["_id"])
            post["url"] = url
            outPosts.append(post)
    
    return render_template('show_entries.html', entries=outPosts, selected_tag=tagname, util=util)





def runServer():
    _app.run()


if __name__ == '__main__':
    
    if _app.config['DEBUG']:
        from werkzeug.wsgi import SharedDataMiddleware

        _app.wsgi_app = SharedDataMiddleware(_app.wsgi_app, {
          '/': os.path.join(os.path.dirname(__file__), 'static')
        })
    
    if len(sys.argv) == 2 and sys.argv[1] == "init":
        print "initializing db."
        init_db()
    else:
        print "running app."
        _app.run(host=_app.config["HOST_NAME"], 
                 port=_app.config["HOST_PORT"], 
                 debug=_app.config["DEBUG"])
    