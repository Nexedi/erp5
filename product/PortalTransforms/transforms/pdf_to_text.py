# -*- coding: utf-8 -*-
"""
Uses the xpdf (www.foolabs.com/xpdf)
"""

from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from Products.PortalTransforms.libtransforms.utils import bin_search, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.commandtransform import popentransform
from Products.PortalTransforms.libtransforms.commandtransform import subprocesstransform
import os

class pdf_to_text(subprocesstransform):
    implements(ITransform)

    __name__ = "pdf_to_text"
    inputs   = ('application/pdf',)
    output  = 'text/plain'
    output_encoding = 'utf-8'

    __version__ = '2004-07-02.01'

    binaryName = "pdftotext"
    binaryArgs = "-enc UTF-8 -layout -nopgbrk %(infile)s -"
    useStdin = False

class old_pdf_to_text(commandtransform):
    implements(ITransform)

    __name__ = "pdf_to_text"
    inputs   = ('application/pdf',)
    output  = 'text/plain'
    output_encoding = 'utf-8'

    binaryName = "pdftotext"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = 'unkown.pdf'

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        text = self.invokeCommand(tmpdir, fullname)
        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
        self.cleanDir(tmpdir)
        cache.setData(text)
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        # FIXME: windows users...
        textfile = "%s/%s.txt" % (tmpdir, sansext(fullname))
        cmd = 'cd "%s" && %s -enc UTF-8 "%s" "%s" 2>error_log 1>/dev/null' % (
            tmpdir, self.binary, fullname, textfile)
        os.system(cmd)
        try:
            text = open(textfile).read()
        except:
            try:
                return open("%s/error_log" % tmpdir, 'r').read()
            except:
                return ''
        return text

def register():
    return pdf_to_text()
