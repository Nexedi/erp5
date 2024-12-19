##############################################################################
#
# Copyright (c) 2024 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly advised to contract a Free Software
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

from erp5.component.document.CxmlDocument import CxmlDocument
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ERP5Type.Permissions import AccessContentsInformation

class CxmlConfirmationRequest(CxmlDocument):
  meta_type = 'ERP5 Cxml Confirmation Request'
  portal_type = 'Cxml Confirmation Request'

  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  security.declareProtected(AccessContentsInformation, 'getConfirmId')
  def getConfirmId(self):
    """
    Get the ConfirmID from the ConfirmationHeader in cXML
    """
    et = self.getElementTree()
    if et is None:
      return
    confirmation_request_header = et.xpath('/cXML/Request/ConfirmationRequest/ConfirmationHeader')[0]
    return confirmation_request_header.get('confirmID')

  security.declareProtected(AccessContentsInformation, 'getLinePropertyDict')
  def getLinePropertyDict(self):
    """
    Get Sale Order Line properties and values from ConfirmationRequest cXML
    """
    #self.validateXML()
    et = self.getElementTree()
    line_dict = {}
    for confirmation_item in et.xpath('/cXML/Request/ConfirmationRequest/ConfirmationItem'):
      property_dict = {}
      property_dict['int_index'] = int_index = int(confirmation_item.get("lineNumber"))
      confirmation_status = confirmation_item.find("ConfirmationStatus")
      start_date = confirmation_status.get("shipmentDate")
      if start_date is not None:
        property_dict['start_date'] = DateTime(start_date)
      stop_date = confirmation_status.get("deliveryDate")
      if stop_date is not None:
        property_dict['stop_date'] = DateTime(stop_date)
      property_dict['quantity'] = float(confirmation_status.get("quantity"))
      line_dict[int_index] = property_dict
    return line_dict
