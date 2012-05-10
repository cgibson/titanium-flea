from flask import Flask
import markdown
import os
from tripy.utils.path import Path
from tifl.md import convert
import settings as s


app = Flask(__name__)

@app.route('/page/<filename>')
def _show_post(filename):
    filename = Path(s.WEB_BASE).abspath() / filename

    try:
        print "fetching %s" % filename
        mdText = convert.convertFile(filename, webBase=s.WEB_BASE, wikiLinkBase="page")
    except ValueError, ve:
        return markdown.markdown("# An error has occurred\n%s" % str(ve))

    return mdText


def runServer(debug=False, config="web.cfg"):
    s.loadSettings(config)
    app.run(debug=s.DEBUG)
