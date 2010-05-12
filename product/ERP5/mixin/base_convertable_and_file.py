# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from OFS.Image import Pdata
import cStringIO

_MARKER = []
class BaseConvertableAndFileMixin:
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                                                                 'getBaseData')
  def getBaseData(self, default=_MARKER):
    """return BaseData as str."""
    if default is _MARKER:
      base_data = self._baseGetBaseData()
    else:
      base_data = self._baseGetBaseData(default)
    if base_data is None:
      return None
    else:
      return str(base_data)

  security.declareProtected(Permissions.ModifyPortalContent, '_setBaseData')
  def _setBaseData(self, data):
    """
      This is a method which combine base_convertable interface and File API
    """
    if not isinstance(data, Pdata) and data is not None:
      file = cStringIO.StringIO(data)
      data, size = self._read_data(file)
      self._setSize(size)
    self._baseSetBaseData(data)
