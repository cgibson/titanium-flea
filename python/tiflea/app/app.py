from __future__ import with_statement

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from tripy.utils.path import Path
import settings as s
import os
from contextlib import closing
import sys

from sqlite3 import dbapi2 as sqlite3

_app = Flask(__name__, template_folder=s.TEMPLATE_DIR, static_folder=s.STATIC_DIR)
_app.config.from_object(s)

def connect_db():
    return sqlite3.connect(_app.config['DATABASE'])


def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with _app.open_resource('schema.sql') as f:
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
    print os.getcwd()
    cur = g.db.execute('select id, title, urltitle, html, author, created, published from entries order by id desc')
    entries = []
    for row in cur.fetchall():
        # skip if not published
        if not row[6]:
            continue
        
        entry = dict(title=row[1], html=row[3], author=row[4], created=row[5])
        
        # Build entry url
        url = "%s/p/%s" % (s.SITE_BASE, row[2])
        entry["url"] = url
        
        # Build tag list
        cur = g.db.execute('select t.name from tags t, tagsXentries x where x.entryid==? and x.tagid==t.id',[row[0]])
        entry["tags"] = [tag[0] for tag in cur.fetchall()]
        entries.append(entry)
        
    #entries = [dict(title=row[0], html=row[1], author=row[2], created=row[3]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@_app.route('/p/<urltitle>')
def single_entry(urltitle):

    cur = g.db.execute('select id, title, html, author, created, published from entries where urltitle==?',[urltitle])
    result = cur.fetchone()
    if not result:
        entry = None
    else:
        entry = dict(title=result[1], html=result[2], author=result[3], created=result[4])
        cur = g.db.execute('select t.name from tags t, tagsXentries x where x.entryid==? and x.tagid==t.id',[result[0]])
        entry["tags"] = [tag[0] for tag in cur.fetchall()]
        
    return render_template('single_entry.html', entry=entry)


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
        url = "%s/p/%s" % (s.SITE_BASE, row[2])
        entry["url"] = url
        
        # Build tag list
        cur = g.db.execute('select t.name from tags t, tagsXentries x where x.entryid==? and x.tagid==t.id',[row[0]])
        entry["tags"] = [tag[0] for tag in cur.fetchall()]
        entries.append(entry)
        
    #entries = [dict(title=row[0], html=row[1], author=row[2], created=row[3]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries, selected_tag=tagname )


def runServer():
    _app.run()


if __name__ == '__main__':
    
    if len(sys.argv) == 2 and sys.argv[1] == "init":
        print "initializing db."
        init_db()
    else:
        print "running app."
        _app.run(host=s.HOST_NAME, port=s.HOST_PORT, debug=s.DEBUG)