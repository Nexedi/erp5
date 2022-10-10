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
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Message import translateString
from Products.ERP5Type import Permissions
from OFS.Image import Pdata
from io import BytesIO
import six
_MARKER = object()

class BaseConvertableFileMixin:
  """
  This class provides a generic implementation of IBaseConvertable.
  This Mixin combine BaseConvertable  and Files documents.
    getBaseData is overridden to serialise Pdata into string
    _setBaseData is overridden to wrap data into Pdata

  - updateBaseMetadata is not implemented in this mixin and must be
  explicitly overridden if needed.

  """

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ModifyPortalContent, 'convertToBaseFormat')
  def convertToBaseFormat(self):
    """
    1 - Check if convertable data is not empty.
    2 - Call implementation of conversion to Base Format
    3 - Call convertFile form processing_status_workflow
        to inform user in case of failures by writing
        error message in transition's comment.
    """
    if not self.hasData():
      # Empty document cannot be converted
      return
    message = self._convertToBaseFormat() # Call implementation method
    if message is None:
      message = translateString('Converted to ${mime_type}.',
                            mapping={'mime_type': self.getBaseContentType()})
    # if processing_status_workflow is associated
    workflow_tool = getToolByName(self.getPortalObject(), 'portal_workflow')
    if workflow_tool.isTransitionPossible(self, 'convert_file'):
      self.convertFile(comment=message) # Invoke workflow method
    return message

  security.declareProtected(Permissions.ModifyPortalContent, 'updateBaseMetadata')
  def updateBaseMetadata(self, **kw):
    """This Method must be defined explicitly.
    """
    raise NotImplementedError

  security.declareProtected(Permissions.AccessContentsInformation,
                                                                 'getBaseData')
  def getBaseData(self, default=_MARKER):
    """Serialise Pdata into bytes
    """
    self._checkConversionFormatPermission(None)
    if default is _MARKER:
      base_data = self._baseGetBaseData()
    else:
      base_data = self._baseGetBaseData(default)
    if base_data is None:
      return None
    else:
      return bytes(base_data)

  security.declareProtected(Permissions.ModifyPortalContent, '_setBaseData')
  def _setBaseData(self, data):
    """Wrap value into Pdata
    """
    if not isinstance(data, Pdata) and data is not None:
      file_ = BytesIO(data)
      data, _ = self._read_data(file_)
    self._baseSetBaseData(data)

InitializeClass(BaseConvertableFileMixin)
