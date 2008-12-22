##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.CMFCore.Expression import Expression

class InventoryConstraint:
  """
  Inventory Constraint
  """
  _constraints = (
    {
    'id': 'duplicate_inventory',
    'type': 'DuplicateInventory',
    },
    { 'id'            : 'category_existence',
      'description'   : 'Destination must be defined',
      'type'          : 'CategoryExistence',
      'portal_type'   : Expression('python: portal.getPortalNodeTypeList()'),
      'destination'        : 1,
      'message_category_not_set': 'Wharehouse must be defined',
    },
    { 'id'            : 'category_existence',
      'description'   : 'Destination section must be defined',
      'type'          : 'CategoryExistence',
      'portal_type'   : Expression('python: portal.getPortalNodeTypeList()'),
      'destination_section' : 1,
      'message_category_not_set': 'Owner must be defined',
    },
    { 'id'            : 'start_date',
      'description'   : 'Start Date must be defined',
      'type'          : 'PropertyExistence',
      'start_date'    : 1,
      'message_property_not_set': 'Inventory Date must be defined',
      'message_no_such_property': 'Inventory Date must be defined',
    },
    { 'id'            : 'resource_on_line',
      'description'   : 'Resource must be defined on all lines',
      'type'          : 'TALESConstraint',
      'expression'    : 'python: None not in [x.getResourceValue() for x in object.getMovementList()]',
      'message_expression_false': 'You must define a resource on all lines',
    },
  )
