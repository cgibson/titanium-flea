import ConfigParser

WEB_BASE  = "www"
PORT      = 5000
SITE_NAME = "Titanium Flea"
DEBUG     = True

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

    WEB_BASE  = cfgObj.get("general", "web_base")
    PORT      = cfgObj.getint("general", "port")
    SITE_NAME = cfgObj.get("general", "site_name")
    DEBUG     = cfgObj.getboolean("general", "debug")

		
