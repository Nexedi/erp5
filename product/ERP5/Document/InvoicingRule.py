##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
      Transformation Sourcing Rule object make sure
      items required in a Transformation are sourced
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
      if parent.getPortalType()=='Applied Rule' and parent.getSpecialiseId()=='default_order_rule':
        return 1
      return 0

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
      LOG('InvoicingRule.expand, my_context_movement.getPhysicalPath()',0,my_context_movement.getPhysicalPath())
      LOG('InvoicingRule.expand, my_context_movement.getSource()',0,my_context_movement.getSource())
      LOG('InvoicingRule.expand, my_context_movement.getTargetSource()',0,my_context_movement.getTargetSource())
      LOG('InvoicingRule.expand, my_context_movement.showDict()',0,my_context_movement.showDict())
      LOG('InvoicingRule.expand, my_context_movement.getSource',0,my_context_movement.getSource())
      if my_context_movement.getSource() is not None:
        # We should only expand movements if they have a source
        # otherwise, it creates infinite recursion
        # This happens for example whenever the source of a movement is acquired
        # from an order which is deleted afterwards
        # LOG('Sourcing', 0, str(my_context_movement.getDefaultResource()))
        new_id = 'invoice_line'
        if new_id in applied_rule.objectIds():
          invoice_line = applied_rule[new_id]
        else:
          invoice_line = applied_rule.newContent(
                type_name = delivery_line_type,
                id = new_id
              )

        resource = my_context_movement.getResource()
        invoice_line._edit(
                price = my_context_movement.getPrice(),
                target_quantity = my_context_movement.getTargetQuantity(),
                target_efficiency = my_context_movement.getTargetEfficiency(),
                resource = resource,
                target_start_date = my_context_movement.getTargetStartDate(),
                target_stop_date = my_context_movement.getTargetStartDate(),
                target_source = my_context_movement.getTargetDestination(),
                target_source_section = my_context_movement.getTargetSourceSection(),
                quantity_unit = my_context_movement.getQuantityUnit(),
                target_destination = my_context_movement.getTargetDestination(),
                target_destination_section = my_context_movement.getTargetDestinationSection(),
                deliverable = 1   # We do need to collect invoice lines to build invoices
            )
        #  transformation_source.setVariationCategoryList(
        #            my_context_movement.getVariationCategoryList())

      # Create one submovement which sources the transformation
      Rule.expand(self, applied_rule, **kw)


    def isDeliverable(self, m):
      resource = m.getResource()
      if m.getResource() is None:
        return 0
      else:
        return 1
