'''
Created on May 26, 2012

@author: cgibson
'''

import settings as s
from tripy.utils.path import Path
from tifl.md import convert

class URLException (Exception):
    
    def __init__(self, *args):
        super(URLException, self).__init__(args)


class BasicRouter (object):
    
    def __init__(self):
        pass
    
    def route(self, url):
        sourceFilePath = Path(s.WEB_BASE).abspath() / url
        return convert.convertFile(sourceFilePath, s.WEB_BASE, s.WIKI_BASE)
        #raise URLException("Unable to route.")
    

class HashedRouter (object):
    
    def __init__(self):
        super(HashedRouter, self).__init__()
        
    def route(self, url):
        
        return self.getCachedUrlContents(url)


    def getCachedUrlContents(self, url):
        sourceFile = Path(s.WEB_BASE).abspath() / url
        
        urlHash = sourceFile.hashStr() + ".html"
        urlHashFile = Path(s.HASH_BASE) / urlHash
        
        if not urlHashFile.exists():
            return convert.convertFile(sourceFile, s.WEB_BASE, s.WIKI_BASE, outputFile=urlHashFile) + "\n\n<hr><p>FIRST_CREATED!!!</p>"
        
        hashStat = urlHashFile.stat()
        sourceStat = sourceFile.stat()
        
        if sourceStat.st_mtime > hashStat.st_mtime:
            return convert.convertFile(sourceFile, s.WEB_BASE, s.WIKI_BASE, outputFile=urlHashFile) + "\n\n<hr><p>OLD CACHE... REBUILDING!!!</p>"
        else:
            fd = urlHashFile.openFile("r")
            text = fd.read()
            fd.close()
            return text + "\n\n<hr><p>CACHED!!! FILE: %s</p>" % urlHashFile
            