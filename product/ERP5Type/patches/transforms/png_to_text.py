from Products.PortalTransforms.interfaces import itransform
from StringIO import StringIO
import PIL.Image
from Products.PortalTransforms.libtransforms.commandtransform \
    import popentransform

import os
import sys
import tempfile

class png_to_text(popentransform):
    __implements__ = itransform
    __name__  = "png_to_text"

    inputs   = ('image/png',)
    output  = 'text/plain'
    output_encoding = 'utf-8'
    
    __version__ = '2008-10-07.01'

    binaryName = "ocrocmd"
    binaryArgs = "%(infile)s "
    useStdin = False

    def convert(self, data, cache, **kwargs):
        # XXX Surcharge from commandtransform, as ocrocmd do not accept 
        # parameters but environnement variable.
        # Surcharging prevent to put the variable in the zope.conf file
        command = "%s %s" % (self.binary, self.binaryArgs)
        if not self.useStdin:
            tmpfile, tmpname = tempfile.mkstemp(text=False) # create tmp
            os.write(tmpfile, data) # write data to tmp using a file descriptor
            os.close(tmpfile)       # close it so the other process can read it
            command = command % { 'infile' : tmpname } # apply tmp name to command

        cin, couterr = os.popen4('quiet=1 hocr=0 %s' % command, 'b')

        if self.useStdin:
            cin.write(str(data))

        status = cin.close()

        out = self.getData(couterr)
        couterr.close()

        if not self.useStdin:
            # remove tmp file
            os.unlink(tmpname)
                     
        cache.setData(out)                                                                                                                             
        return cache       

def register():
    return png_to_text()
