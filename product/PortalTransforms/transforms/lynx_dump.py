"""
Uses lynx -dump
"""
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.commandtransform import popentransform
import os
from zope.interface import implements

class lynx_dump(popentransform):
    implements(itransform)

    __name__ = "lynx_dump"
    inputs   = ('text/html',)
    output  = 'text/plain'
    
    __version__ = '2004-07-02.1'

    binaryName = "lynx"
    # XXX does -stdin work on windows?
    binaryArgs = "-dump -crawl -stdin"
    useStdin = True
    
    def getData(self, couterr):
        lines = [ line for line in couterr.readlines() ]
        return ''.join(lines[3:])

class old_lynx_dump(commandtransform):
    implements(itransform)

    __name__ = "lynx_dump"
    inputs   = ('text/html',)
    output  = 'text/plain'

    binaryName = "lynx"
    binaryArgs = "-dump"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = 'unknown.html'
        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        outname = "%s/%s.txt" % (tmpdir, orig_name)
        self.invokeCommand(tmpdir, fullname, outname)
        text = self.astext(outname)
        self.cleanDir(tmpdir)
        cache.setData(text)
        return cache

    def invokeCommand(self, tmpdir, inputname, outname):
        os.system('cd "%s" && %s %s "%s" 1>"%s" 2>/dev/null' % \
               (tmpdir, self.binary, self.binaryArgs, inputname, outname))

    def astext(self, outname):
        txtfile = open("%s" % (outname), 'r')
        txt = txtfile.read()
        txtfile.close()
        return txt

def register():
    return lynx_dump()
