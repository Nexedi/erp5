##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

from erp5.component.document.MovementGroup import MovementGroup

class InvoiceMovementGroup(MovementGroup):
  """
  This movement group is used to collect movements related to the same
  invoice. This movement group should be used in delivery level.
  """
  meta_type = 'ERP5 Invoice Movement Group'
  portal_type = 'Invoice Movement Group'

  def _getPropertyDict(self, movement, **kw):
    return dict(_invoice_uid=self._getInvoiceUid(movement))

  def test(self, document, property_dict, property_list=None, **kw):
    if property_dict['_invoice_uid'] != document.getUid():
      return False, {}
    else:
      return True, {}

  def _getInvoiceUid(self, simulation_movement):
    parent_rule = simulation_movement.getParentValue()
    portal = self.getPortalObject()
    invoice_movement_types = portal.getPortalInvoiceMovementTypeList()
    while not parent_rule.isRootAppliedRule():
      parent_simulation_movement = parent_rule.getParentValue()
      grand_parent_rule = parent_simulation_movement.getParentValue()
      parent_delivery = parent_simulation_movement.getDeliveryValue()
      if parent_delivery is not None and \
             parent_delivery.getPortalType() in invoice_movement_types:
        return parent_delivery.getExplanationValue().getUid()
      parent_rule = grand_parent_rule
    return None
