# -*- coding: utf-8 -*-
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.libtransforms.commandtransform \
    import commandtransform
import os
import subprocess
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
    useStdin = False

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
      kwargs['filename'] = 'input.tiff'
      tmp_dir, input_file = self.initialize_tmpdir(data,
                                   filename='input.tiff')

      text = None
      try:
        output_file_path = os.path.join(tmp_dir, 'output')
        cmd = self.binary, input_file, output_file_path
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,)
        stdout = process.communicate()[0]
        err = process.returncode
        if err:
          if err < 0:
            exit_msg = 'killed with signal %s' % -err
          else:
            exit_msg = 'exited with status %s' % err
          raise EnvironmentError('Command %r %s. Command output:\n%s'
                                 % (cmd, exit_msg, stdout))

        output_file = open(output_file_path + '.txt', 'r')
        out = output_file.read()
        output_file.close()
      finally:
        self.cleanDir(tmp_dir)

      data = datastream('output.txt')
      data.setData(out.rstrip()) # .rstrip() also removes page breaks
      return data

def register():
    return tiff_to_text()
