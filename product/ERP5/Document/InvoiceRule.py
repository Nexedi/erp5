##############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.Document.DeliveryRule import DeliveryRule

from zLOG import LOG

class InvoiceRule(DeliveryRule):
    """
      Invoice Rule object make sure an Invoice in the simulation
      is consistent with the real invoice
      WARNING: what to do with movement split ?
    """

    # CMF Type Definition
    meta_type = 'ERP5 Invoice Rule'
    portal_type = 'Invoice Rule'
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

    # Simulation workflow
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, force=0, **kw):
      """
        Expands the current movement downward.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      invoice_line_type = 'Simulation Movement'
      # Get the invoice where we come from
      my_invoice = applied_rule.getDefaultCausalityValue()
      # Only expand if my_invoice is not None and 
      # state is not 'confirmed'
      if my_invoice is not None:
        # Only expand invoice rule if invoice not yet confirmed 
        # (This is consistent with the fact that once simulation is 
        # launched, we stick to it)
        if force or \
           (applied_rule.getLastExpandSimulationState() not in \
                     self.getPortalReservedInventoryStateList() and \
           applied_rule.getLastExpandSimulationState() not in \
                      self.getPortalCurrentInventoryStateList()):
          # First, check each contained movement and make
          # a list of invoice_line ids which do not need to be copied
          # eventually delete movement which do not exist anylonger
          existing_uid_list = []
          movement_type_list = applied_rule.getPortalMovementTypeList()
          # non generic
          invoice_movement_type_list = \
                                 applied_rule.getPortalInvoiceMovementTypeList()
          for movement in applied_rule.contentValues(
                   filter={'portal_type':movement_type_list}):
            invoice_element = movement.getDeliveryValue(
                   portal_type=invoice_movement_type_list)

            if (invoice_element is None) or\
               (invoice_element.hasCellContent()) or\
               (len(invoice_element.getDeliveryRelatedValueList()) > 1):
              # Our invoice_element is already related 
              # to another simulation movement
              # Delete ourselve
  #             movement.flushActivity(invoke=0)
              # XXX Make sure this is not deleted if already in delivery
              applied_rule._delObject(movement.getId())  
            else:
              existing_uid_list_append(invoice_element.getUid())
          # Copy each movement (line or cell) from the invoice
          # non generic
          for invoice_line_object in my_delivery.getMovementList(
                   portal_type=self.getPortalInvoiceMovementTypeList()):
            try:
              # Only create if orphaned movement
              if invoice_line_object.getUid() not in existing_uid_list:
                # Generate a nicer ID
                if invoice_line_object.getParentUid() ==\
                                      invoice_line_object.getExplanationUid():
                  # We are on a line
                  new_id = invoice_line_object.getId()
                else:
                  # On a cell
                  new_id = "%s_%s" % (invoice_line_object.getParentId(),
                                      invoice_line_object.getId())
                # Generate the simulation movement
                new_sim_mvt = applied_rule.newContent(
                                portal_type=invoice_line_type,
                                id=new_id,
                                order_value=invoice_line_object,
                                delivery_value=invoice_line_object,
                                # XXX Do we need to copy the quantity
                                # Why not the resource, the variation,...
                                quantity=invoice_line_object.getQuantity(),
                                delivery_ratio=1,
                                deliverable=1)
            except AttributeError:
              LOG('ERP5: WARNING', 0, 
                  'AttributeError during expand on invoice line %s' \
                  % invoice_line_object.absolute_url())
          # Now we can set the last expand simulation state to the 
          # current state
          applied_rule.setLastExpandSimulationState(
              my_invoice.getSimulationState())
      # Pass to base class
      Rule.expand(self, applied_rule, force=force, **kw)
