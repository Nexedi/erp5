import re, os, tempfile
import uno
import unohelper
from com.sun.star.beans import PropertyValue

from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.utils import bodyfinder, scrubHTML

class document(commandtransform):

    def __init__(self, name, data):
        """ Initialization: create tmp work directory and copy the
        document into a file"""
 
        commandtransform.__init__(self, name)
        name = self.name()
        self.tmpdir, self.fullname = self.initialize_tmpdir(data, filename=name)
        self.outputfile = self.fullname + '.html'

    def convert(self):
        """Convert the document"""

        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                       'com.sun.star.bridge.UnoUrlResolver', localContext )
        ctx = resolver.resolve(
                       'uno:socket,host=localhost,port=2002;'
                       'urp;StarOffice.ComponentContext')
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
                       'com.sun.star.frame.Desktop', ctx)

        # load the document
        url = unohelper.systemPathToFileUrl(self.fullname)
        doc = desktop.loadComponentFromURL(url, '_blank', 0, ())

        filterName = 'swriter: HTML (StarWriter)'
        storeProps = (
                       PropertyValue('FilterName', 0, filterName, 0),
                      )

        # pre-create a empty file for security reason
        url = unohelper.systemPathToFileUrl(self.outputfile)
        doc.storeToURL(url, storeProps)

        try:
            doc.close(True)
        except com.sun.star.util.CloseVetoException:
            pass

        # maigic to release some resource
        ctx.ServiceManager

    def html(self):
        htmlfile = open(self.outputfile, 'r')
        html = htmlfile.read()
        htmlfile.close()
        html = scrubHTML(html)
        body = bodyfinder(html)
        return body
