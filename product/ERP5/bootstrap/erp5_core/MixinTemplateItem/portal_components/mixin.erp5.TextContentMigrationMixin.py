# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import six

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Utils import guessEncodingFromText, str2bytes, unicode2str

from erp5.component.document.Document import _MARKER

def _parseContentType(content_type):
  if not content_type:
    return ('', [])

  # RFC2045, 5.1.  Syntax of the Content-Type Header Field
  parts = content_type.split(";")
  content_type = parts.pop(0)
  extensions = dict((x.split("=")[0], x.split("=")[1]) for x in parts)
  return (content_type, extensions)

def _serializeContentType(content_type, extensions):
  parts = [content_type] + ["=".join(x) for x in extensions.items()]
  return "; ".join(parts)

class TextContentMigrationMixin:
  """
  Defines setters and getters related to `text_content` (string). These methods
  were defined by Property Sheets before and have been deprecated with a
  migration path to `data` (bytes) provided by the mixin.

  This mixin is *not* fully transparent: it explicitely redefined `getData` and
  `setData` and expects them not to be redefined. Instead, use the lower-level
  `_getData` and `_setData` which will be called by the mixin.
  """

  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation, 'hasTextContent')
  def hasTextContent(self):
    """
    Having text content is having data
    """
    return self.hasData()

  security.declarePrivate('_getTextContent')
  def _getTextContent(self, default=_MARKER, encoding='utf-8'):
    """
    Return data as string. Both Py2 and Py3 should return 'str' type object.
    """
    data = self.getData(default)
    if data is None:
      return None

    # Encoding is set, in order of priority, by parameter, then content type,
    # then guessing. If nothing works, use UTF-8.
    content_type = self.getContentType()
    if encoding is None and content_type:
      (content_type, extensions) = _parseContentType(content_type)
      if "charset" in extensions:
        encoding = extensions["charset"]

    if encoding is None:
      encoding = guessEncodingFromText(data) or 'utf-8'

    text_content = data.decode(encoding)
    if six.PY2 and isinstance(text_content, six.text_type):
      text_content = unicode2str(text_content, encoding=encoding)

    return text_content

  security.declareProtected(Permissions.AccessContentsInformation, 'getTextContent')
  getTextContent = _getTextContent

  security.declarePrivate('_setTextContent')
  def _setTextContent(self, text_content, encoding='utf-8', **kw):
    """
    Setting text content is like setting data, but with a string argument.
    Slightly different from `getTextContent`: Py3 accepts 'str', but Py2
    supports both bytes (ie. str) and unicode.
    """
    data = text_content
    if data is not None:
      if six.PY2 and isinstance(data, six.text_type):
        data = unicode2str(data, encoding=encoding)
      data = str2bytes(data, encoding=encoding)

    # Add charset information to content type, allows decoding more easily
    content_type = self.getContentType()
    if content_type and content_type.startswith("text/"):
      (content_type, extensions) = _parseContentType(content_type)
      extensions["charset"] = encoding
      self.setContentType(_serializeContentType(content_type, extensions))

    self.setData(data, **kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'setTextContent')
  setTextContent = _setTextContent

  security.declareProtected(Permissions.AccessContentsInformation, 'getData')
  def getData(self, default=_MARKER):
    # type: (bytes) -> bytes | PData
    """
    Goal: `getData` must returns original content.

    On a new instance, `data` will always hold original content, but for old
    instances, the original data could be stored in both `data`, or directly in
    `text_content`. The heuristic is to assume that `text_content` was always
    updated.
    """
    data = None

    try:
      text_content = aq_base(self).text_content or None
    except AttributeError:
      text_content = None

    # Opportunistic migration from `text_content` to `data`
    if text_content is not None:
      data = str2bytes(text_content)
      if _checkPermission(Permissions.ModifyPortalContent, self):
        self.setData(data)
    else:
      if getattr(self, "_getData", None) is not None:
        data = self._getData(default)
      else:
        data = self._baseGetData(default)

    return data

  security.declareProtected(Permissions.ModifyPortalContent, 'setData')
  def setData(self, value, **kw):
    """
    Handles taking care of the backward compatibility fix on `getData`:
    if data is first set, we need to erase text content without ever
    converting.
    """
    try:
      del aq_base(self).text_content
    except AttributeError:
      pass

    self._setData(value, **kw)

InitializeClass(TextContentMigrationMixin)