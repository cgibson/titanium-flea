import ConfigParser

WEB_BASE  = "www"
PORT      = 5000
SITE_NAME = "Titanium Flea"
DEBUG     = True
HASH_BASE = "hash"
WIKI_BASE = "page"

def loadSettings(cfgFiles):
    if not isinstance(cfgFiles, list):
        cfgFiles = [cfgFiles]

    # TODO: add defaults
    cfgObj = ConfigParser.ConfigParser()
    cfgObj.read(cfgFiles)

    global WEB_BASE
    global PORT
    global SITE_NAME
    global DEBUG
    global HASH_BASE
    global WIKI_BASE

    WEB_BASE  = cfgObj.get("general", "web_base")
    PORT      = cfgObj.getint("general", "port")
    SITE_NAME = cfgObj.get("general", "site_name")
    DEBUG     = cfgObj.getboolean("general", "debug")
    HASH_BASE = cfgObj.get("general", "hash_base")
    WIKI_BASE = cfgObj.get("general", "wiki_base")