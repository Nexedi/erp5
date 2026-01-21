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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import bytes2str, str2bytes

from erp5.component.document.Document import _MARKER

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
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'hasTextContent')
  def hasTextContent(self):
    """
    Having text content is having data
    """
    return self.hasData()

  security.declarePrivate('_getTextContent')
  def _getTextContent(self, default=_MARKER):
    """
    Return data as string. Both Py2 and Py3 should return 'str' type object.
    """
    return bytes2str(self.getData(default))

  security.declareProtected(Permissions.AccessContentsInformation, 'getTextContent')
  getTextContent = _getTextContent

  security.declarePrivate('_setTextContent')
  def _setTextContent(self, text_content, **kw):
    """
    Setting text content is like setting data, but with a string argument.
    Slightly different from `getTextContent`: Py3 accepts 'str', but Py2
    supports both bytes (ie. str) and unicode.
    """
    self.setData(text_content.encode(encoding='utf-8', errors='strict'), **kw)

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
        self.edit(
          data=data,
          force_update=True,
        )
        del aq_base(self).text_content
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