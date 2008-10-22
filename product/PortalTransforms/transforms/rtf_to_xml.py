"""
Uses the http://sf.net/projects/rtf2xml bin to do its handy work

"""
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
import os

class rtf_to_xml(commandtransform):
    __implements__ = itransform

    __name__ = "rtf_to_xml"
    inputs   = ('application/rtf',)
    output  = 'text/xml'

    binaryName = "rtf2xml"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = 'unknown.rtf'

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        xml = self.invokeCommand(tmpdir, fullname)
        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
        self.cleanDir(tmpdir)
        cache.setData(xml)
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        # FIXME: windows users...
        xmlfile = "%s/%s.xml" % (tmpdir, sansext(fullname))
        cmd = 'cd "%s" && %s -o %s "%s" 2>error_log 1>/dev/null' % (
            tmpdir, self.binary, xmlfile, fullname)
        os.system(cmd)
        try:
            xml = open(xmlfile).read()
        except:
            try:
                return open("%s/error_log" % tmpdir, 'r').read()
            except:
                return ''
        return xml

def register():
    return rtf_to_xml()
