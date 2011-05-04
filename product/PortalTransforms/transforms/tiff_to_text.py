# -*- coding: utf-8 -*-
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.libtransforms.commandtransform \
    import commandtransform
import os
import tempfile
from zope.interface import implements

class tiff_to_text(commandtransform):
    implements(ITransform)
    __name__  = "tiff_to_text"

    inputs   = ('image/tiff',)
    output  = 'text/plain'
    output_encoding = 'utf-8'

    __version__ = '2011-02-01.01'

    binaryName = "tesseract"
    binaryArgs = "%(infile)s "

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
      kwargs['filename'] = 'input.tiff'
      tmp_dir, input_file = self.initialize_tmpdir(data, 
                                   filename='input.tiff')

      text = None
      try:
        command = self.binary
        output_file_path = os.path.join(tmp_dir, 'output')
        cmd = '%s %s %s' % (
            self.binary, input_file, output_file_path)
        os.system(cmd)
        output_file = open(output_file_path + '.txt', 'r')
        out = output_file.read()
        output_file.close()
      finally:
        self.cleanDir(tmp_dir)

      data = datastream('output.txt')
      data.setData(out)
      return data

def register():
    return tiff_to_text()
