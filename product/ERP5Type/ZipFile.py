##############################################################################
#
# Copyright (c) 2012 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
"""
Restricted zipfile module.

From restricted python, use "import zipfile" (see patches/Restricted.py).
"""
from past.builtins import basestring
from AccessControl import allow_class as _allow_class
from zExceptions import Unauthorized
import zipfile as _zipfile

BadZipfile = _zipfile.BadZipfile
_allow_class(BadZipfile)
LargeZipFile = _zipfile.LargeZipFile
_allow_class(LargeZipFile)

ZIP64_LIMIT = _zipfile.ZIP64_LIMIT
ZIP_FILECOUNT_LIMIT = _zipfile.ZIP_FILECOUNT_LIMIT
ZIP_MAX_COMMENT = _zipfile.ZIP_MAX_COMMENT

ZIP_STORED = _zipfile.ZIP_STORED
ZIP_DEFLATED = _zipfile.ZIP_DEFLATED

ZipInfo = _zipfile.ZipInfo
_allow_class(ZipInfo)
ZipExtFile = _zipfile.ZipExtFile
_allow_class(ZipExtFile)

def _disallowed(*args, **kw):
  raise Unauthorized

def _zipfile__init__(self, file, mode="r", compression=ZIP_STORED, allowZip64=False):
  if isinstance(file, basestring):
    raise ValueError('"file" must be a file-like object')
  super(self.__class__, self).__init__(file, mode=mode, compression=compression, allowZip64=allowZip64)

_zipfile_dict = {
  '__init__': _zipfile__init__,
  'write': _disallowed,
  'extract': _disallowed,
  'extractall': _disallowed,
  'printdir': lambda self: None,
}

ZipFile = type('ZipFile', (_zipfile.ZipFile, object), _zipfile_dict)
_allow_class(ZipFile)
PyZipFile = type('PyZipFile', (_zipfile.PyZipFile, object), _zipfile_dict)
_allow_class(PyZipFile)
