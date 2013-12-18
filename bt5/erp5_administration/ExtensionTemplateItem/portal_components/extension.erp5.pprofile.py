import pprofile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_quopri
from cStringIO import StringIO
import os

_allsep = os.sep + (os.altsep or '')
def _relpath(name):
  return os.path.normpath(os.path.splitdrive(name)[1]).lstrip(_allsep)

class ZopeBase(object):
  __allow_access_to_unprotected_subobjects__ = 1
  def _getFilename(self, filename, f_globals):
    if 'Script (Python)' in filename:
      try:
        script = f_globals['script']
      except KeyError:
        pass
      else:
        filename = script.id
    return filename

  def asMIMEString(self):
    """
    Return a mime-multipart representation of both callgrind profiling
    statistics and all involved source code.
    Avoids relying on a tempfile, as a zipfile/tarfile would require.
    To unpack resulting file, see "unpack a MIME message" in
      http://docs.python.org/2/library/email-examples.html
    """
    result = MIMEMultipart()

    out = StringIO()
    self.callgrind(out, relative_path=True)
    profile = MIMEApplication(out.getvalue(), 'x-kcachegrind', encode_quopri)
    profile.add_header(
      'Content-Disposition',
      'attachment',
      filename='cachegrind.out.pprofile',
    )
    result.attach(profile)

    for name, lines in self.iterSource():
      lines = ''.join(lines)
      if lines:
        pyfile = MIMEText(lines, 'x-python')
        pyfile.add_header(
          'Content-Disposition',
          'attachment',
          filename=_relpath(name),
        )
        result.attach(pyfile)

    return result.as_string(), result['content-type']

class ZopeProfiler(ZopeBase, pprofile.Profile):
  pass

class ZopeStatisticalProfile(ZopeBase, pprofile.StatisticalProfile):
  pass

class ZopeStatisticalThread(pprofile.StatisticalThread):
  __allow_access_to_unprotected_subobjects__ = 1

def getProfiler(verbose=False, **kw):
  """
  Get a Zope-friendly pprofile.Profile instance.
  """
  return ZopeProfiler(**kw)

def getStatisticalProfilerAndThread(**kw):
  """
  Get Zope-friendly pprofile.StatisticalProfile and pprofile.StatisticalThread
  instances. Arguments are forwarded to StatisticalThread.__init__ .
  """
  profiler = ZopeStatisticalProfile()
  return profiler, ZopeStatisticalThread(
    profiler=profiler,
    **kw
  )
