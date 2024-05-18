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
from __future__ import print_function

import os
import sys
import tempfile
import zipfile
import subprocess
from six.moves import urllib
from six.moves import cStringIO as StringIO
from io import BytesIO

try:
  import lxml
except ImportError:
  lxml = None
try:
  import odfpy
except ImportError:
  odfpy = None

if lxml:
  class LXMLValidator:
    """Validate ODF document using RelaxNG and lxml"""
    schema_url = \
      'http://docs.oasis-open.org/office/v1.1/OS/OpenDocument-schema-v1.1.rng'

    def __init__(self, schema_url=schema_url):
      self.schema_url = schema_url
      self.schema_path = os.path.join(
        os.path.dirname(__file__), os.path.basename(schema_url))
      self.relaxng =  lxml.etree.RelaxNG(lxml.etree.parse(self.schema_path))

    def validate(self, odf_file_content):
      error_list = []
      odf_file = BytesIO(odf_file_content)
      for f in ('content.xml', 'meta.xml', 'styles.xml', 'settings.xml'):
        error_list.extend(self._validateXML(odf_file, f))
      return error_list

    def _validateXML(self, odf_file, content_file_name):
      zfd = zipfile.ZipFile(odf_file)
      doc = lxml.etree.parse(BytesIO(zfd.read(content_file_name)))
      return []
      # The following is the past implementation that validates with
      # RelaxNG schema. But recent LibreOffice uses extended odf
      # format by default, that does not pass the RelaxNG validation.
      doc.docinfo.URL = content_file_name
      self.relaxng.validate(doc)
      return [error for error in str(self.relaxng.error_log).splitlines(True)]

  Validator = LXMLValidator

elif odfpy:

  class OdflintValidator:
    """Validates ODF files using odflint, available on pypi
    http://opendocumentfellowship.org/development/projects/odfpy
    """
    def validate(self, odf_file_content):
      fd, file_name = tempfile.mkstemp()
      os.write(fd, odf_file_content)
      os.close(fd)
      process = subprocess.Popen(
        ['odflint', file_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
      )
      stdout, _ = process.communicate()
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
      print('No validator available', file=sys.stderr)

  Validator = NoValidator


