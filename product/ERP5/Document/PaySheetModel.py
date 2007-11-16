##############################################################################
#
# Copyright (c) 2007, Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.TradeCondition import TradeCondition
from Products.ERP5.Document.DeliveryLine import DeliveryLine

class PaySheetModel(TradeCondition, DeliveryLine):
    """
      PaySheetModel are used to define calculating rules specific to a 
      date, a convention, a enmployees group...
      This permit to applied a whole of calculating rules on a whole of
      pay sheets
    """

    meta_type = 'ERP5 Pay Sheet Model'
    portal_type = 'Pay Sheet Model'
    isPredicate = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Folder
                      , PropertySheet.Comment
                      , PropertySheet.Arrow
                      , PropertySheet.TradeCondition
                      , PropertySheet.Order
                      , PropertySheet.PaySheetModel
                      , PropertySheet.MappedValue
                      , PropertySheet.Amount
                      , PropertySheet.DefaultAnnotationLine
                      )

    def getRatioQuantityFromReference(self, ratio_reference=None):
      """
      return the ratio value correponding to the ratio_reference,
      or description if ratio value is empty,
      None if ratio_reference not found
      """
      object_ratio_list = self.contentValues(portal_type=\
          'Pay Sheet Model Ratio Line')
      for object in object_ratio_list:
        if object.getReference() == ratio_reference:
          if not object.getQuantity():
            return object.getDescription()
          else:
            return object.getQuantity()
      return None 

    def getRatioQuantityList(self, ratio_reference_list):
      """
      Return a list of reference_ratio_list correponding values.
      reference_ratio_list is a list of references to the ratio lines
      we want to get.
      """
      if type(ratio_reference_list) != type([]):
        return None
      return [self.getRatioQuantityFromReference(reference) \
          for reference in ratio_reference_list]

