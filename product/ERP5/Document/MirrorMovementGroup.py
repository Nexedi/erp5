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

from Products.ERP5.Document.MovementGroup import MovementGroup

class MirrorMovementGroup(MovementGroup):
  """
  For Payment Transaction, we don't care the direction:

    * source:A, destination:B, quantity:+10
    * source:B, destination:A, quantity:-10

  The purpose of MirrorMovementGroup is to make to merge these two
  simulation movements into one delivery movement. To do that, we need
  to reverse the order with the help of Mapped Property document that
  exists in the rule.
  """
  meta_type = 'ERP5 Mirror Movement Group'
  portal_type = 'Mirror Movement Group'

  def _getPropertyDict(self, movement, **kw):
    return {}

  def test(self, document, property_dict, **kw):
    return True, property_dict

  def _separate(self, movement_list):
    # record if mirrored or not in simulation movements.
    mapping_dict = {}
    if len(movement_list) == 0:
      return []
    for movement in movement_list:
      if _isMirrored(movement):
        applied_rule = movement.getParentValue()
        # XXX do we need more precise way to find Mapped Property
        # document for mirrored?
        mapping_list = mapping_dict.setdefault(
          applied_rule,
          applied_rule.getSpecialiseValue().objectValues(
          portal_type='Mapped Property') or [])
        if len(mapping_list) > 0:
          movement.setPropertyMappingValue(mapping_list[0])
    return [[movement_list, {}]]

def _isMirrored(document):
  # to merge A->B and B->A movements, here we determine if we need to
  # reverse or not by just comparing its source_section's id and
  # destination_section's id, whose result should be consistent for each
  # document.
  return document.getDestinationSectionId() > document.getSourceSectionId()
