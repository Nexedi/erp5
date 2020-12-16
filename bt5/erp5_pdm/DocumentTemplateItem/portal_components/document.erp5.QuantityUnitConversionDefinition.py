##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Permissions import AccessContentsInformation
from Products.ERP5Type.XMLObject import XMLObject


class QuantityUnitConversionDefinition(XMLObject):
  """
    Quantity Unit Conversion Definition
  """

  meta_type = 'ERP5 Quantity Unit Conversion Definition'
  portal_type = 'Quantity Unit Conversion Definition'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.QuantityUnitConversionDefinition
                    )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTitle')
  def getTitle(self):
    """
      Set a title that includes the Quantity Unit
    """
    default_title = self._baseGetTitle()

    quantity_unit = self.getQuantityUnitValue()
    if quantity_unit is not None:
      # only the last part is relevant
      return "%s Definition" % quantity_unit.getTitle()

    return default_title

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConversionRatio')
  def getConversionRatio(self):
    """
      Compute conversion ratio associated with this definition
    """
    quantity = self.getQuantity()

    if quantity != 0 and self.isInverse():
      quantity = 1.0/quantity

    return quantity
