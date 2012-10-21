from __future__ import with_statement

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from tripy.utils.path import Path
import os
import sys
from werkzeug.contrib.atom import AtomFeed
import iso8601
from tiflea import util
import datetime
from tiflea.post import Post
import couchdb
import tiflea.settings as blogsettings
#from sqlite3 import dbapi2 as sqlite3

_app = Flask(__name__)
#_app.config.from_object(s)

# Load override configuration values into flask config
#
override = Path("config.py")
root = Path(_app.root_path)
if not override.exists():
    raise ValueError("No config file found")

_app.config.from_pyfile(str(override.abspath()))

_app.template_folder = _app.config["TEMPLATE_DIR"]
_app.static_folder = _app.config["STATIC_DIR"]

def connect_db(db_name):
    #return sqlite3.connect(_app.config['DATABASE'])
    couch = couchdb.Server(_app.config["DB_HOST"])
    couch.resource.credentials = _app.config["DB_AUTH"]
    return couch[db_name]


db = connect_db(_app.config["DB_NAME"])
settings = blogsettings.loadSettings(db)
for k,v in settings.iteritems():
    if k[0] == "_":
        continue
    _app.config[k] = v


@_app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db(_app.config["DB_NAME"])
    g.settings = blogsettings.loadSettings()


@_app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    #if hasattr(g, 'db'):
    #    g.db.close()


@_app.route('/')
def show_entries():
    
    print _app.config["blog_title"]
    
    #cur = g.db.execute('select id, title, urltitle, html, author, created, published from entries order by id desc')
    #Post.by_date.sync(g.db)
    #Post.by_tag.sync(g.db)
    posts = Post.by_date(g.db, descending=True)
    #results = g.db.view("blog/by_title")
    outPosts = []
    for post in posts:
    #for row in cur.fetchall():
        # skip if not published
        if not post["published"]:
            continue
        
        # Create a datetime object from our timestamp.
        d = iso8601.parse_date( post["date"] )
        """
        months = ["jan", "feb", "mar", "apr",
                  "may", "jun", "jul", "aug", 
                  "sep", "oct", "nov", "dec"]
        
        post["created_month"] = months[d.month - 1]
        post["created_day"] = d.day
        """
        
        post["date_str"] = d.strftime("%B %d, %Y")
        # Build entry url
        url = "%s/p/%s" % (_app.config["SITE_BASE"], post["_id"])
        post["url"] = url
        
        outPosts.append(post)

    return render_template('show_entries.html', entries=outPosts, util=util, title="View Recent Posts")

@_app.route('/feed')
def feed():

    feed = AtomFeed('Mr.Voxel Articles',
                    feed_url=request.url, url=request.url_root)

    posts = Post.by_date(g.db, descending=True)

    for post in posts:
    #for row in cur.fetchall():
        # skip if not published
        if not post["published"]:
            continue

        # Build entry url
        url = "%s/p/%s" % (_app.config["SITE_BASE"], post["_id"])
        
        feed.add(post.title, 
                 unicode(post.html), 
                 content_type="html",
                 author=post.author,
                 url=url,
                 updated=post.date,
                 published=post.date
                 )

    return feed.get_response()


@_app.route('/p/<post_id>')
def single_entry(post_id):

    #cur = g.db.execute('select id, title, urltitle, html, author, created, published from entries where urltitle==?',[urltitle])
    #result = cur.fetchone()
    post = Post.load(g.db, post_id)
    
    # Create a datetime object from our timestamp.
    d = iso8601.parse_date( post["date"] )
    """
    months = ["jan", "feb", "mar", "apr",
              "may", "jun", "jul", "aug", 
              "sep", "oct", "nov", "dec"]
    
    post["created_month"] = months[d.month - 1]
    post["created_day"] = d.day
    """
    
    post["date_str"] = d.strftime("%B %d, %Y")
    
    # Build entry url
    url = "%s/p/%s" % (_app.config["SITE_BASE"], post["_id"])
    post["url"] = url
    
    description = None
    if "description" in post:
        description = post["description"]

    return render_template('single_entry.html', entry=post, util=util, title=post["title"], description=description)


@_app.route('/t/<tagname>')
def tag_entries(tagname):
    
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
            d = iso8601.parse_date( post["date"] )
            """
            months = ["jan", "feb", "mar", "apr",
                      "may", "jun", "jul", "aug", 
                      "sep", "oct", "nov", "dec"]
            
            post["created_month"] = months[d.month - 1]
            post["created_day"] = d.day
            """
            post["date_str"] = d.strftime("%B %d, %Y")
            
            # Build entry url
            url = "%s/p/%s" % (_app.config["SITE_BASE"], post["_id"])
            post["url"] = url
            outPosts.append(post)
    
    return render_template('show_entries.html', entries=outPosts, selected_tag=tagname, util=util, title="Sort by Tag - %s" % tagname)



@_app.route('/c/<category>')
def category_entries(category):
    
    # We're sure we're only getting one value here
    results = Post.by_cat(g.db, key=category)
    outPosts = []
    
    for posts in results:
        
        # Now that we finally have all of the post data, iterate through the list
        for post in posts:

            # skip if not published
            if not post["published"]:
                continue
            
            # Create a datetime object from our timestamp.
            d = iso8601.parse_date( post["date"] )
            """
            months = ["jan", "feb", "mar", "apr",
                      "may", "jun", "jul", "aug", 
                      "sep", "oct", "nov", "dec"]
            
            post["created_month"] = months[d.month - 1]
            post["created_day"] = d.day
            """
            post["date_str"] = d.strftime("%B %d, %Y")
            
            # Build entry url
            url = "%s/p/%s" % (_app.config["SITE_BASE"], post["_id"])
            post["url"] = url
            outPosts.append(post)
    
    return render_template('show_entries.html', entries=outPosts, selected_cat=category, util=util, title="Sort by Category - %s" % category)





def runServer():
    _app.run()


if __name__ == '__main__':
    
    if _app.config['DEBUG']:
        from werkzeug.wsgi import SharedDataMiddleware

        _app.wsgi_app = SharedDataMiddleware(_app.wsgi_app, {
          '/': os.path.join(os.path.dirname(__file__), 'static')
        })

    print "running app."
    _app.run(host=_app.config["HOST"], 
             port=_app.config["PORT"], 
             debug=_app.config["DEBUG"])
    