# -*- coding: utf-8 -*-
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.libtransforms.commandtransform \
    import popentransform
from subprocess import Popen, PIPE
import os
import tempfile
from zope.interface import implementer

@implementer(ITransform)
class png_to_text(popentransform):
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
        command = self.binary
        environment = {'quiet': '1',
                       'hocr': '0',
                       'blockwise': '0'}
        if not self.useStdin:
            tmpfile, tmpname = tempfile.mkstemp(text=False) # create tmp
            os.write(tmpfile, data) # write data to tmp using a file descriptor
            os.close(tmpfile)       # close it so the other process can read it
            popen = Popen([command, tmpname], env=environment, stdout=PIPE)
            out = popen.communicate()[0]

        else:
            popen = Popen([command, tmpname], env=environment, stdin=PIPE,
                                                                   stdout=PIPE)
            out = popen.communicate(bytes(data))[0]

        if not self.useStdin:
            # remove tmp file
            os.unlink(tmpname)

        cache.setData(out)
        return cache

def register():
    return png_to_text()
