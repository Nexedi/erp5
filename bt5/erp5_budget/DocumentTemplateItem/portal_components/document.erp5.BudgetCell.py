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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5.Document.MetaNode import MetaNode
from Products.ERP5.Document.Movement import Movement

class BudgetCell(Predicate, MetaNode, Movement):
    """ Budget Cell defines a cell of budget.
    XXX This is not a Movement, but we need getDestinationCredit
    XXX This is not a MetaNode
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
                      , PropertySheet.MappedValue
                      , PropertySheet.VariationRange
                      )

    # CMF Type Definition
    meta_type='ERP5 Budget Cell'
    portal_type='Budget Cell'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    security.declareProtected(Permissions.AccessContentsInformation, 'getTitle')
    def getTitle(self):
      """
      Return a calculated title.
      """
      script = self._getTypeBasedMethod('asTitle')
      if script is not None:
        return script()
      raise UnboundLocalError,\
              "Did not find title script for portal type: %r" %\
              self.getPortalType()

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventory')
    def getCurrentInventory(self, at_date=None, **kw):
      """ Returns current inventory.

      at_date parameter can be used to take into account budget transactions
      before that date.
      """
      kw['node_uid'] = self.getUid()
      resource = self.getResourceValue()
      if resource is not None:
        kw['resource_uid'] = resource.getUid()
      if at_date:
        kw['at_date'] = at_date
      sign = self.getParentValue().BudgetLine_getConsumptionSign()
      return sign * self.portal_simulation.getCurrentInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentBalance')
    def getCurrentBalance(self, at_date=None):
      """
      Returns current balance
      """
      sign = self.getParentValue().BudgetLine_getConsumptionSign()
      return sign * self.getQuantity(0.0) + self.getCurrentInventory(at_date=at_date)

    security.declareProtected(Permissions.AccessContentsInformation, 'getConsumedBudget')
    def getConsumedBudget(self, src__=0):
      """
      Return consumed budget.
      """
      script = self._getTypeBasedMethod('getConsumedBudget')
      if script is not None:
        return script(src__=src__)
      raise UnboundLocalError,\
              "Did not find consumed budget script for portal type: %r" % \
              self.getPortalType()

    security.declareProtected(Permissions.AccessContentsInformation, 'getAvailableBudget')
    def getAvailableBudget(self, at_date=None):
      """
      Return available budget.
      """
      return self.getCurrentBalance(at_date=at_date) - self.getEngagedBudget()

    security.declareProtected(Permissions.AccessContentsInformation, 'getEngagedBudget')
    def getEngagedBudget(self, src__=0):
      """
      Return Engaged budget.
      """
      script = self._getTypeBasedMethod('getEngagedBudget')
      if script is not None:
        return script(src__=src__)
      raise UnboundLocalError,\
              "Did not find engaged budget script for portal type: %r" % \
              self.getPortalType()

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getExplanationValue')
    def getExplanationValue(self, default=None):
      """Explanation has no meaning for a budget cell"""
      return default

    security.declareProtected(Permissions.ModifyPortalContent,
                              'setSourceCredit')
    def setSourceCredit(self, source_credit):
      """Set the quantity.
      Overloaded from movement, we always set the quantity, even if not passed
      """
      try:
        source_credit = float(source_credit)
      except TypeError:
        source_credit = 0.0
      Movement.setSourceCredit(self, source_credit)

    def setSourceDebit(self, source_debit):
      """Set the quantity.
      Overloaded from movement, we always set the quantity, even if not passed
      """
      try:
        source_debit = float(source_debit)
      except TypeError:
        source_debit = 0.0
      Movement.setSourceDebit(self, source_debit)

    security.declareProtected( Permissions.ModifyPortalContent,
                               'setDestinationDebit', 'setDestinationCredit' )
    setDestinationDebit = setSourceCredit
    setDestinationCredit = setSourceDebit
