##############################################################################
#
# Copyright (c) 2005, 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.DeliveryLine import DeliveryLine
from Products.ERP5.Document.Amount import Amount
from zLOG import LOG

class BudgetTransaction(DeliveryLine):
    """
    BudgetTransaction an order or transfer of budget.
    """

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.VariationRange
                      , PropertySheet.ItemAggregation
                      )
    # CMF Type Definition
    meta_type='ERP5 Budget Transaction'
    portal_type='Budget Transaction'    
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)


    security.declareProtected(Permissions.AccessContentsInformation, 
                              'isAccountable')
    def isAccountable(self):
      """
      Supersedes the DeliveryLine definition
      """
      return 1

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getSimulationState')
    def getSimulationState(self):
      """
      Supersedes the DeliveryLine definition
      """
      return self.portal_workflow.getInfoFor(self, 'simulation_state')
