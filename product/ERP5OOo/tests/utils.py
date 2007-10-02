##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

"""This module provides utilities for testing ODF files.

Validator: a class defining a `validate` method that expects odf file content
as first argument and returns list of errors.

"""

import os
import sys
import tempfile
import zipfile
import popen2
import urllib2
from cStringIO import StringIO

try:
  import libxml2
except ImportError:
  libxml2 = None
try:
  import odfpy
except ImportError:
  odfpy = None


if libxml2:

  class ErrorHandler:
    """Collect errors"""
    def __init__(self, file_name):
      libxml2.lineNumbersDefault(1)
      self.file_name = file_name
      self.error_list = []

    def onError(self, msg, data):
      line = libxml2.lastError().line()
      self.error_list.append('%s:%s: %s' % (self.file_name, line, msg))
    onWarning = onError


  class LibXML2Validator:
    """Validate ODF document using RelaxNG and libxml2"""
    schema_url = \
      'http://docs.oasis-open.org/office/v1.1/OS/OpenDocument-schema-v1.1.rng'

    def __init__(self, schema_url=schema_url):
      self.schema_url = schema_url
      self.schema_path = os.path.join(
              tempfile.gettempdir(), 'OpenDocument.rng')
      # download if local copy does not exists
      if not os.path.exists(self.schema_path):
        self._download()
      ctxt = libxml2.relaxNGNewParserCtxt(self.schema_path)
      self.relaxng = ctxt.relaxNGParse()

    def validate(self, odf_file_content):
      error_list = []
      odf_file = StringIO(odf_file_content)
      for f in ('content.xml', 'meta.xml', 'styles.xml', 'settings.xml'):
        error_list.extend(self._validateXML(odf_file, f))
      return error_list

    def _download(self):
      r = urllib2.urlopen(self.schema_url)
      out_file = open(self.schema_path, 'w')
      try:
        out_file.write(r.read())
      finally:
        out_file.close()
        r.close()

    def _validateXML(self, odf_file, content_file_name):
      validationCtxt = self.relaxng.relaxNGNewValidCtxt()
      err = ErrorHandler(content_file_name)

      validationCtxt.setValidityErrorHandler(
          err.onError, err.onWarning)

      zfd = zipfile.ZipFile(odf_file)
      content = zfd.read(content_file_name)

      validationCtxt.relaxNGValidateDoc(
                libxml2.parseMemory(content, len(content)))
      return err.error_list

  Validator = LibXML2Validator

elif odfpy:

  class OdflintValidator:
    """Validates ODF files using odflint, available on pypi
    http://opendocumentfellowship.org/development/projects/odfpy
    """
    def validate(self, odf_file_content):
      fd, file_name = tempfile.mkstemp()
      os.write(fd, odf_file_content)
      os.close(fd)
      stdout, stdin = popen2.popen4('odflint %s' % file_name)
      stdin.close()
      error_list = ''
      for line in stdout:
        if line.startswith('Error: '):
          error_list += line
      os.unlink(file_name)
      return error_list

  Validator = OdflintValidator

else:

  class NoValidator:
    """Does not actually validate, but keep the interface."""
    def validate(self, odf_file_content):
      print >> sys.stderr, 'No validator available'

  Validator = NoValidator


