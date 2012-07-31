from __future__ import with_statement

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import markdown
import os
from tripy.utils.path import Path
import settings as s
from contextlib import closing
import sys

from sqlite3 import dbapi2 as sqlite3
import __main__

app = Flask(__name__)
app.config.from_object(s)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def show_entries():
    cur = g.db.execute('select id, title, html, author, created, published from entries order by id desc')
    entries = []
    for row in cur.fetchall():
        # skip if not published
        if not row[5]:
            continue
        
        entry = dict(title=row[1], html=row[2], author=row[3], created=row[4])
        cur = g.db.execute('select t.name from tags t, tagsXentries x where x.entryid==? and x.tagid==t.id',[row[0]])
        entry["tags"] = [tag[0] for tag in cur.fetchall()]
        print entry["tags"]
        entries.append(entry)
        
    #entries = [dict(title=row[0], html=row[1], author=row[2], created=row[3]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

"""
@app.route('/page/<filename>')
def _show_post(filename):

    try:
        print "fetching %s" % filename
        mdText = router.route("pages/" + filename)
    except ValueError, ve:
        return markdown.markdown("# An error has occurred\n%s" % str(ve))
"""
"""
@app.route('/page/<filename>')
def _show_post(filename):

    try:
        print "fetching %s" % filename
        mdText = router.route("pages/" + filename)
    except ValueError, ve:
        return markdown.markdown("# An error has occurred\n%s" % str(ve))

    return mdText
"""


"""
def runServer(debug=False, config="web.cfg"):
    s.loadSettings(config)
    app.run(debug=s.DEBUG)
"""

if __name__ == '__main__':
    
    if len(sys.argv) == 2 and sys.argv[1] == "init":
        print "initializing db."
        init_db()
    else:
        print "running app."
        app.run()