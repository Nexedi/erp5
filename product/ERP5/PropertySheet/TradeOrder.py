##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#          Alexandre Boeglin  <alex@nexedi.com>
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

class TradeOrder:
  """
  Constraints that can be enforced on Trade Orders
  """

  _properties = (
  )

  _categories = (
  )

  _constraints = (
    { 'id'            : 'source_section_category_existence',
      'description'   : 'Source section must be defined',
      'type'          : 'CategoryExistence',
      'portal_type'   : ('Person', 'Organisation'),
      'source_section': 1,
      'message_category_not_set': 'Supplier must be defined',
    },
    { 'id'            : 'destination_section_category_existence',
      'description'   : 'Destination section must be defined',
      'type'          : 'CategoryExistence',
      'portal_type'   : ('Person', 'Organisation'),
      'destination_section': 1,
      'message_category_not_set': 'Client must be defined',
    },
    { 'id'            : 'source_category_existence',
      'description'   : 'Source must be defined',
      'type'          : 'CategoryExistence',
      'portal_type'   : ('Person', 'Organisation'),
      'source': 1,
      'message_category_not_set': 'Sender or Provider must be defined',
    },
    { 'id'            : 'destination_category_existence',
      'description'   : 'Destination must be defined',
      'type'          : 'CategoryExistence',
      'portal_type'   : ('Person', 'Organisation'),
      'destination': 1,
      'message_category_not_set': 'Recipient or Beneficiary must be defined',
    },
    { 'id'            : 'price_currency_category_existence',
      'description'   : 'Price Currency must be defined',
      'type'          : 'CategoryExistence',
      'portal_type'   : ('Currency', ),
      'price_currency': 1,
      'message_category_not_set': 'Currency must be defined',
    },
    { 'id'            : 'total_quantity',
      'description'   : 'Total Quantity must not be 0',
      'type'          : 'TALESConstraint',
      'expression'    : 'python: object.getTotalQuantity() > 0',
      'message_expression_false': 'Total Quantity must not be 0',
    },
    { 'id'            : 'start_date',
      'description'   : 'Start Date must be defined',
      'type'          : 'PropertyExistence',
      'start_date'    : 1,
      'message_no_such_property' : "Shipping Date must be defined",
      'message_property_not_set' : "Shipping Date must be defined",
    },
    { 'id'            : 'date_coherency',
      'description'   : 'Stop Date must be after Start Date',
      'type'          : 'TALESConstraint',
      'expression'    : 'python: object.getStopDate() >= object.getStartDate()',
      'message_expression_false': 'Delivery Date must be after Shipping Date',
    },
    { 'id'            : 'lines',
      'description'   : 'Lines must be defined',
      'type'          : 'ContentExistence',
      'portal_type'   : Expression('portal/getPortalOrderMovementTypeList'),
      'message_no_subobject_portal_type' : \
                                'At least one line is required',
    },
  )
