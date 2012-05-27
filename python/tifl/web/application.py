from flask import Flask
import markdown
import os
from tripy.utils.path import Path
from tifl.md import convert
import settings as s
from router import HashedRouter

app = Flask(__name__)

router = HashedRouter()

@app.route('/page/<filename>')
def _show_post(filename):

    try:
        print "fetching %s" % filename
        mdText = router.route("pages/" + filename)
    except ValueError, ve:
        return markdown.markdown("# An error has occurred\n%s" % str(ve))

    return mdText


def runServer(debug=False, config="web.cfg"):
    s.loadSettings(config)
    app.run(debug=s.DEBUG)
