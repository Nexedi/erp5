import sys

def sendRawToCups(self, printer_name, raw_string, number_copies=1):
  """
    Send ouput to printer as raw string
  """
  if sys.platform == 'win32':
     # No idea what to do at this point
     pass
  else:
     from popen2 import popen2
     import tempfile
     tempdir = tempfile.tempdir
     tempfile.tempdir = '/tmp'
     newraw_path = tempfile.mktemp(suffix='.cups' )
     f = open(newraw_path, 'w')
     f.write(raw_string)
     f.close()
     tempfile.tempdir = tempdir
     imgout, imgin = popen2('lp -h 192.1.2.5 -d %s -n %i %s'
                                       % (printer_name, number_copies, newraw_path))
     imgin.write('')
     imgin.close()
     imgout.read()
     imgout.close()

