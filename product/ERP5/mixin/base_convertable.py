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
from Products.ERP5Type.Base import WorkflowMethod
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions

class BaseConvertableMixin:
  """
  This class provides a generic implementation of IBaseConvertable.
  """

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ModifyPortalContent, 'convertToBaseFormat')
  def convertToBaseFormat(self):
    """
    """
    if not self.hasData():
      # Empty document cannot be converted
      return
    try:
      message = self._convertToBaseFormat() # Call implemetation method
      if message is None:
        message = self.Base_translateString('Converted to ${mime_type}.',
                              mapping={'mime_type': self.getBaseContentType()})
      self.convertFile(comment=message) # Invoke workflow method
    except NotImplementedError:
      message = ''
    return message

  security.declareProtected(Permissions.ModifyPortalContent, 'updateBaseMetadata')
  def updateBaseMetadata(self, **kw):
    """
    """
    raise NotImplementedError

  def convertFile(self, **kw):
    """
    Workflow transition invoked when conversion occurs.
    Usefull for document instances which are not associated
    to processing_status_workflow like TempObject.
    """
  convertFile = WorkflowMethod(convertFile)
