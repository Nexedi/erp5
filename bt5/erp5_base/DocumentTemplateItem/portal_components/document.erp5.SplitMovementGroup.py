
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

from erp5.component.document.MovementGroup import MovementGroup

class SplitMovementGroup(MovementGroup):
  """
  This movement group is used to split all the movements that are aggregated
  by the Simulation Select Method.

  XXX-Tatuya: However this test() method returns True, so the aggregated
  movements can be inserted into existing Delivery/Line/Cell that are aggregated
  by the Delivery Select Method. What use case this is applied for?

  * Reference:
  http://www.erp5.org/HowToConfigureMovementGroup

  test(self, object, property_dict, **kw):
    (mandatory)
    This method returns if object can be used for updating according to
    property_dict. Its return value is [updatable? (True or False),
    property_dict that is used to update values]. If you want to create a
    new Delivery/Line/Cell instead of updating existing one,
    return [False, property_dict].

  """
  meta_type = 'ERP5 Split Movement Group'
  portal_type = 'Split Movement Group'

  def _getPropertyDict(self, movement, **kw):
    return {}

  def test(self, document, property_dict, **kw):
    return True, property_dict

  def _separate(self, movement_list, **kw):
    return [[[movement], {}] for movement in movement_list]
