##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
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

class ShopOrder:
  """
    ShopOrder properties and categories
  """

  _properties = (
    { 'id'          : 'address',
      'description' : 'Address',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'city',
      'description' : 'City',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'country',
      'description' : 'Country',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'email',
      'description' : 'Email',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'exchange_fee',
      'description' : 'Exchange Fee',
      'type'        : 'int',
      'mode'        : 'w' },
    { 'id'          : 'extra_fee',
      'description' : 'Extra Fee',
      'type'        : 'int',
      'mode'        : 'w' },
    { 'id'          : 'name',
      'description' : 'Name',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'organisation',
      'description' : 'Organisation',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'order_id',
      'description' : 'Order Id',
      'type'        : 'int',
      'mode'        : 'w' },
    { 'id'          : 'phone',
      'description' : 'Phone',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'send_fee',
      'description' : 'Send Fee',
      'type'        : 'int',
      'mode'        : 'w' },
    { 'id'          : 'send_fee_title',
      'description' : 'Send Fee Title',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'price',
      'description' : 'Price',
      'type'        : 'int',
      'mode'        : 'w' },
    { 'id'          : 'total_price',
      'description' : 'Total Price',
      'type'        : 'int',
      'mode'        : 'w' },
    { 'id'          : 'vat',
      'description' : 'Vat',
      'type'        : 'int',
      'mode'        : 'w' },
    { 'id'          : 'euvat',
      'description' : 'Euvat',
      'type'        : 'int',
      'mode'        : 'w' },
    { 'id'          : 'zip_code',
      'description' : 'Zip Code',
      'type'        : 'string',
      'mode'        : 'w' },
  )

  _categories = ( )
