##############################################################################
#
# Copyright (c) 2006-2017 Nexedi SA and Contributors. All Rights Reserved.
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

# Cloudooo uses zip= argument, which is also a python builtin
# pylint: disable=redefined-builtin

from erp5.component.document.Document import DocumentConversionServerProxy
from base64 import b64encode, b64decode
from zExceptions import Unauthorized
from Products.ERP5Type.Utils import bytes2str

def convertDocumentByConversionServer(
    self,
    data,
    source_mimetype,
    destination_mimetype,
    zip=False,
    refresh=False,
    conversion_kw=None,
    REQUEST=None
  ):
  if REQUEST is not None:
    raise Unauthorized

  proxy = DocumentConversionServerProxy(self)
  return b64decode(
    proxy.convertFile(
      bytes2str(b64encode(data)),
      source_mimetype,
      destination_mimetype,
      zip,
      refresh,
      conversion_kw or {}
    )
  )