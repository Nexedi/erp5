"""
Uses the http://sf.net/projects/pdftohtml bin to do its handy work

"""
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from Products.PortalTransforms.libtransforms.utils import bin_search, \
  bodyfinder, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.commandtransform import popentransform
import os

class popen_pdf_to_html(popentransform):
    implements(ITransform)

    __version__ = '2004-07-02.01'

    __name__ = "pdf_to_html"
    inputs   = ('application/pdf',)
    output  = 'text/html'
    output_encoding = 'utf-8'

    binaryName = "pdftohtml"
    binaryArgs = "%(infile)s -noframes -stdout -enc UTF-8"
    useStdin = False

    def getData(self, couterr):
        return bodyfinder(couterr.read())

class pdf_to_html(commandtransform):
    implements(ITransform)

    __name__ = "pdf_to_html"
    inputs   = ('application/pdf',)
    output  = 'text/html'
    output_encoding = 'utf-8'

    binaryName = "pdftohtml"
    binaryArgs = "-noframes -enc UTF-8"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = 'unknown.pdf'

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
        if os.name=='posix':
            cmd = 'cd "%s" && %s %s "%s" 2>error_log 1>/dev/null' % (
                   tmpdir, self.binary, self.binaryArgs, fullname)
        else:
            cmd = 'cd "%s" && %s %s "%s"' % (
                  tmpdir, self.binary, self.binaryArgs, fullname)
        os.system(cmd)
        try:
            htmlfilename = os.path.join(tmpdir, sansext(fullname) + '.html')
            htmlfile = open(htmlfilename, 'r')
            html = htmlfile.read()
            htmlfile.close()
        except:
            try:
                return open("%s/error_log" % tmpdir, 'r').read()
            except:
                return "transform failed while running %s (maybe this pdf file doesn't support transform)" % cmd
        return html

def register():
    return pdf_to_html()
