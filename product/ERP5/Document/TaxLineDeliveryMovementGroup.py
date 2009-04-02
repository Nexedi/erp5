##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5.Document.MovementGroup import MovementGroup

class TaxLineDeliveryMovementGroup(MovementGroup):
  """
  This movement group is used to group movements for tax lines, they should end
  up in the same invoice than the corresponding invoice line.
  """
  meta_type = 'ERP5 Tax Line Delivery Movement Group'
  portal_type = 'Tax Line Delivery Movement Group'

  def _getPropertyDict(self, movement, **kw):
    return dict(tax_line_delivery=self._getTaxLineDelivery(movement))

  def test(self, movement, property_dict, **kw):
    tax_line_delivery = self._getTaxLineDelivery(movement)
    if tax_line_delivery == property_dict['tax_line_delivery'] or None in (
          tax_line_delivery, property_dict['tax_line_delivery']):
      return True, property_dict
    return False, property_dict

  def _getTaxLineDelivery(self, movement):
    # computes the delivery that should be used for this tax line
    if movement.getPortalType() == 'Simulation Movement':
      delivery_line = None
      applied_rule = movement.getParentValue()
      
      for other_rule in applied_rule.getParentValue().contentValues():
        if other_rule.getSpecialiseValue().getPortalType() == 'Tax Rule':
          continue
        
        invoice_simulation_movement_list = other_rule.contentValues()
        # if there is only one movement, it's easy.
        if len(invoice_simulation_movement_list) == 1:
          delivery_line = \
            invoice_simulation_movement_list[0].getDeliveryValue()

          # unless it has been splitted, then it might be from another line ..
          if 'split' in movement.getId():
            original_movement_id = movement.getId().split('_')[0]
            original_movement = applied_rule._getOb(original_movement_id)
            other_movement_list = [x for x in
                  original_movement.getDeliveryValue().getDeliveryRelatedValueList()
                  if x != original_movement]
            if other_movement_list:
              other_movement = other_movement_list[0]
              other_movement_applied_rule = [ar for ar in 
                    other_movement.getParentValue().getParentValue().contentValues()
                 if ar.getSpecialiseValue().getPortalType() != 'Tax Rule'][0]
              for other_movement_applied_rule_simulation_movement in\
                    other_movement_applied_rule.contentValues():
                if 'split' in \
                    other_movement_applied_rule_simulation_movement.getId():
                  delivery_line =\
                     other_movement_applied_rule_simulation_movement.getDeliveryValue()
        else:
          # otherwise, it might be a split, then we do dirty heuristics to find
          # the corresponding invoice simulation movement and delivery.
          # Once again, this will only work if invoice lines are built before
          # tax lines.
          if 'split' in movement.getId():
            invoice_simulation_movement_list = [m for m in
                invoice_simulation_movement_list if 'split' in m.getId()]
            if len(invoice_simulation_movement_list) == 1:
              delivery_line = \
                invoice_simulation_movement_list[0].getDeliveryValue()
          else:
            invoice_simulation_movement_list = [m for m in
                invoice_simulation_movement_list if 'split' not in m.getId()]
            if len(invoice_simulation_movement_list) == 1:
              delivery_line = \
                invoice_simulation_movement_list[0].getDeliveryValue()

      # in case of invoice rule (ie. starting from Invoice)
      if delivery_line is None:
        delivery_line = applied_rule.getParentValue().getOrderValue()

      # in case of invoicing rule (ie. starting from Order)
      if delivery_line is None:
        delivery_line = movement.getParentValue().getParentValue().getDeliveryValue()

      if delivery_line is not None:
        return delivery_line.getExplanationValue().getRelativeUrl()

    elif movement.getPortalType() in self.getPortalDeliveryTypeList():
      # "movement" is actually a delivery here, we're trying to update
      return movement.getRelativeUrl()
    return None

