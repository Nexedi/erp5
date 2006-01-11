##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.Document.MetaNode import MetaNode


from zLOG import LOG

class BudgetCell(Predicate, MetaNode ):
    """
       BudgetCell ...
    """

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.SimpleItem
                      , PropertySheet.Folder
                      , PropertySheet.Predicate
                      , PropertySheet.SortIndex
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Amount
                      , PropertySheet.Budget
                      )

    # CMF Type Definition
    meta_type='ERP5 Budget Cell'
    portal_type='Budget Cell'    
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    security.declareProtected(Permissions.View, 'getTitle')
    def getTitle(self):
	    cat_value = self.getPortalObject().portal_categories.getCategoryValue
	    return '/'.join([cat_value(x).getTitle()
			    for x in self.getMembershipCriterionCategoryList()])
    
    security.declareProtected(Permissions.View, 'getCurrentInventory')  
    def getCurrentInventory(self):
      return  self.portal_simulation.getCurrentInventory(node=self.getRelativeUrl())

    security.declareProtected(Permissions.View, 'getCurrentBalance')
    def getCurrentBalance(self):
      return self.getQuantity(0.0) + self.portal_simulation.getCurrentInventory(node=self.getRelativeUrl())
    security.declareProtected(Permissions.View, 'getConsumedBudget')
    def getConsumedBudget(self, src__=0):
      financial_section = self.getMembershipCriterionCategoryList()[0]
      function = self.getMembershipCriterionCategoryList()[1]
      group = self.getMembershipCriterionCategoryList()[2]
      return self.portal_simulation.getAvailableInventory(
            src__ = src__,  
            financialSectionCategory = self.portal_categories.getCategoryValue(financial_section).getUid(),
            functionCategory = self.portal_categories.getCategoryValue(function).getUid(),
            groupCategory = self.portal_categories.getCategoryValue(group).getUid(),
            date = {'query' : [self.getParent().getParent().getStartDate(), self.getParent().getParent().getStopDate()], 'range' : 'minmax'},
           )
