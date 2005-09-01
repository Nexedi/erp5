##############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG

class InvoicingRule(Rule):
    """
      Invoicing Rule expand simulation created by a order rule.
    """

    # CMF Type Definition
    meta_type = 'ERP5 Invoicing Rule'
    portal_type = 'Invoicing Rule'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      )

    security.declareProtected(Permissions.AccessContentsInformation, 'test')
    def test(self, movement):
      """
        Tests if the rule (still) applies
      """
      parent = movement.getParent()
      result = 0
      if (parent.getPortalType() == 'Applied Rule') and \
         (parent.getSpecialiseId() == 'default_order_rule'):
        result = 1
      return result

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, **kw):
      """
        Expands the current movement downward.
        -> new status -> expanded
        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      delivery_line_type = 'Simulation Movement'
      # Source that movement from the next node / stock
      my_context_movement = applied_rule.getParent()
      if my_context_movement.getSource() is not None:
        # We should only expand movements if they have a source
        # otherwise, it creates infinite recursion
        # This happens for example whenever the source of a movement is 
        # acquired from an order which is deleted afterwards
        new_id = 'inv_mvt'
        if new_id in applied_rule.objectIds():
          invoice_line = applied_rule[new_id]
        else:
          invoice_line = applied_rule.newContent(
            type_name = delivery_line_type,
            id = new_id
          )
        # Edit movement
        invoice_line._edit(
          price = my_context_movement.getPrice(),
          quantity = my_context_movement.getQuantity(),
          quantity_unit = my_context_movement.getQuantityUnit(),
          efficiency = my_context_movement.getEfficiency(),
          resource = my_context_movement.getresource(),
          variation_category_list = my_context_movement.\
                                            getVariationCategoryList(),
          start_date = my_context_movement.getStartDate(),
          stop_date = my_context_movement.getStartDate(),
          source = my_context_movement.getSource(),
          source_section = my_context_movement.getSourceSection(),
          destination = my_context_movement.getDestination(),
          destination_section = my_context_movement.getDestinationSection(),
          # We do need to collect invoice lines to build invoices
          deliverable = 1   
        )
      # Create one submovement which sources the transformation
      Rule.expand(self, applied_rule, **kw)

    def isDeliverable(self, m):
      resource = m.getResource()
      if m.getResource() is None:
        return 0
      else:
        return 1
