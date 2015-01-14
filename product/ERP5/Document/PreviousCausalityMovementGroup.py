##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

from Products.ERP5.Document.FirstCausalityMovementGroup import \
     FirstCausalityMovementGroup
from zLOG import LOG

class PreviousCausalityMovementGroup(FirstCausalityMovementGroup):
  """
  Group by previous causality. For movements going to Sale Invoices,
  the previous causality is SPL
  """
  meta_type = 'ERP5 Previous Causality Movement Group'
  portal_type = 'Previous Causality Movement Group'

  causality_portal_type = 'Sale Packing List'

  def test(self, movement, property_dict, **kw):
    """Compare explanation to now if it is possible to update delivery"""
    explanation = property_dict.get('_explanation','')
    if movement == movement.getDeliveryValue():
      # We are at delivery level, check if the explanation is part of the causality
      delivery = movement
      if explanation in delivery.getCausalityList():
        return True, {}
      else:
        return False, {}
    raise NotImplementedError("What should we do ?")

  def _getPropertyDict(self, movement, **kw):
    property_dict = super(PreviousCausalityMovementGroup, self).\
        _getPropertyDict(movement, **kw)
    return property_dict
