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

class ParentExplanationMovementGroup(MovementGroup):
  """
  The purpose of MovementGroup is to define how movements are grouped,
  and how values are updated from simulation movements.

  This movement group was first created for building Sale invoices
  transactions lines. We need to put accounting lines in the same
  invoices than invoice lines.
  """
  meta_type = 'ERP5 Parent Explanation Movement Group'
  portal_type = 'Parent Explanation Movement Group'

  def _getPropertyDict(self, movement, **kw):
    property_dict = {}
    parent_explanation_value = movement.getParentExplanationValue()
    property_dict['parent_explanation_value'] = parent_explanation_value
    return property_dict

  def test(self, document, property_dict, **kw):
    if document.getParentExplanationValue() == \
       property_dict['parent_explanation_value']:
      return True, property_dict
    else:
      return False, property_dict
