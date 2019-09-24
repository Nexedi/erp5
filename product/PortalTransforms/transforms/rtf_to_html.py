"""
Uses the http://freshmeat.net/projects/rtfconverter/ bin to do its handy work
"""

from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from Products.PortalTransforms.libtransforms.utils import bin_search, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.ERP5Type.Utils import bodyfinder
import os

class rtf_to_html(commandtransform):
    implements(ITransform)

    __name__ = "rtf_to_html"
    inputs   = ('application/rtf',)
    output  = 'text/html'

    binaryName = "rtf-converter"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = 'unknow.rtf'

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        html = self.invokeCommand(tmpdir, fullname)
        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
        self.cleanDir(tmpdir)
        cache.setData(bodyfinder(html))
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        # FIXME: windows users...
        htmlfile = "%s/%s.html" % (tmpdir, sansext(fullname))
        cmd = 'cd "%s" && %s -o %s "%s" 2>error_log 1>/dev/null' % (
            tmpdir, self.binary, htmlfile, fullname)
        os.system(cmd)
        try:
            html = open(htmlfile).read()
        except:
            try:
                return open("%s/error_log" % tmpdir, 'r').read()
            except:
                return ''
        return html

def register():
    return rtf_to_html()
