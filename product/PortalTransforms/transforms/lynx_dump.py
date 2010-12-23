"""
Uses lynx -dump
"""
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.commandtransform import popentransform
import os

class lynx_dump(popentransform):
    implements(ITransform)

    __name__ = "lynx_dump"
    inputs   = ('text/html',)
    output  = 'text/plain'
    
    __version__ = '2004-07-02.1'

    binaryName = "lynx"
    # XXX does -stdin work on windows?
    binaryArgs = "-dump -stdin -force_html"
    useStdin = True
    
class old_lynx_dump(commandtransform):
    implements(ITransform)

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
