##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type import Permissions, PropertySheet, Interface
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.Document.PaySheetLine import PaySheetLine

from zLOG import LOG

class PaySheetModelLine(PaySheetLine, Predicate):
    """
      A PaySheetModelLine object allows to implement lines in
      PaySheetModel.
      A PaySheetModelLine contain all parameters witch make it possible to
      calculate a service contribution.
    """

    meta_type = 'ERP5 Pay Sheet Model Line'
    portal_type = 'Pay Sheet Model Line'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.VariationRange
                      , PropertySheet.MappedValue
                      , PropertySheet.ValueAddedTax
                      , PropertySheet.EcoTax
                      , PropertySheet.CopyrightTax
                      , PropertySheet.PaySheetModelLine
                      , PropertySheet.Predicate
                      )
