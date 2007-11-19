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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.TradeCondition import TradeCondition
from Products.ERP5Type.XMLMatrix import XMLMatrix


class PaySheetModel(TradeCondition, XMLMatrix):
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

