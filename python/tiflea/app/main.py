from __future__ import with_statement

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from tripy.utils.path import Path
import settings as s
import os
from contextlib import closing
import sys
from werkzeug.contrib.atom import AtomFeed
import datetime
from tiflea import util

from sqlite3 import dbapi2 as sqlite3

_app = Flask(__name__, template_folder=s.TEMPLATE_DIR, static_folder=s.STATIC_DIR)
_app.config.from_object(s)

# Load override configuration values into flask config
#
override = Path("config.py")
root = Path(_app.root_path)
if override.exists():
    _app.config.from_pyfile(str(override.abspath()))


def connect_db():
    return sqlite3.connect(_app.config['DATABASE'])


def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with _app.open_resource('../../scripts/schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@_app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()


@_app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@_app.route('/')
def show_entries():
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
        url = "%s/p/%s" % (_app.config["SITE_BASE"], row[2])
        entry["url"] = url
        
        # Build tag list
        cur = g.db.execute('select t.name from tags t, tagsXentries x where x.entryid==? and x.tagid==t.id',[row[0]])
        entry["tags"] = [tag[0] for tag in cur.fetchall()]
        entries.append(entry)

    return render_template('show_entries.html', entries=entries, util=util)

@_app.route('/feed')
def feed():

    feed = AtomFeed('Mr.Voxel Articles',
                    feed_url=request.url, url=request.url_root)

    cur = g.db.execute('select id, title, urltitle, html, author, created, modified from entries order by id desc')

    for row in cur.fetchall():
        # skip if not published
        if not row[6]:
            continue
        
        title = row[1]
        html = row[3]
        author = row[4]
        
        created = row[5]
        toks = created.split("-")
        created = datetime.datetime(int(toks[0]), int(toks[1]), int(toks[2]))
        
        modified = row[6]
        toks = modified.split("-")
        modified = datetime.datetime(int(toks[0]), int(toks[1]), int(toks[2]))
        
        url = "%s/p/%s" % (_app.config["SITE_BASE"], row[2])
        
        feed.add(title, 
                 unicode(html), 
                 content_type="html",
                 author=author,
                 url=url,
                 updated=modified,
                 published=created
                 )

    return feed.get_response()


@_app.route('/p/<urltitle>')
def single_entry(urltitle):

    cur = g.db.execute('select id, title, urltitle, html, author, created, published from entries where urltitle==?',[urltitle])
    result = cur.fetchone()
    if not result:
        entry = None
    else:
        entry = dict(title=result[1], html=result[3], author=result[4], created=result[5])
        
        url = "%s/p/%s" % (_app.config["SITE_BASE"], result[2])
        entry["url"] = url
        
        months = ["jan", "feb", "mar", "apr",
                  "may", "jun", "jul", "aug", 
                  "sep", "oct", "nov", "dec"]
        
        date_tokens = entry["created"].split("-")
        entry["created_month"] = months[int(date_tokens[1]) - 1]
        entry["created_day"] = date_tokens[2]
        
        cur = g.db.execute('select t.name from tags t, tagsXentries x where x.entryid==? and x.tagid==t.id',[result[0]])
        entry["tags"] = [tag[0] for tag in cur.fetchall()]
        
    return render_template('single_entry.html', entry=entry, util=util)


@_app.route('/t/<tagname>')
def tag_entries(tagname):
    cur = g.db.execute('select e.id, e.title, e.urltitle, e.html, e.author, e.created, e.published ' +
                       ' from entries e, tags t, tagsXentries x ' +
                       ' where x.tagid==t.id and x.entryid=e.id and t.name==? ' +
                       ' order by e.id desc', [tagname])
    entries = []
    for row in cur.fetchall():
        # skip if not published
        if not row[6]:
            continue
        
        entry = dict(title=row[1], html=row[3], author=row[4], created=row[5])
        
        # Build entry url
        url = "%s/p/%s" % (_app.config["SITE_BASE"], row[2])
        entry["url"] = url
        
        months = ["jan", "feb", "mar", "apr",
                  "may", "jun", "jul", "aug", 
                  "sep", "oct", "nov", "dec"]
        
        date_tokens = entry["created"].split("-")
        entry["created_month"] = months[int(date_tokens[1]) - 1]
        entry["created_day"] = date_tokens[2]
        
        # Build tag list
        cur = g.db.execute('select t.name from tags t, tagsXentries x where x.entryid==? and x.tagid==t.id',[row[0]])
        entry["tags"] = [tag[0] for tag in cur.fetchall()]
        entries.append(entry)
        
    #entries = [dict(title=row[0], html=row[1], author=row[2], created=row[3]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries, selected_tag=tagname, util=util)





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
    