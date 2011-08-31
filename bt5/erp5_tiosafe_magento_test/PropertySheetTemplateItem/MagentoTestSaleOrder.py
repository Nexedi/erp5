##############################################################################
#
# Copyright (c) 2002-2011 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

class MagentoTestSaleOrder:
  """
      MagentoTestSaleOrder properties for all ERP5 objects
  """

  _properties = (
      {   'id'          : 'order_id',
          'type'        : 'string',
          'mode'        : 'w' },
      {   'id'          : 'increment_id',
          'type'        : 'string',
          'mode'        : 'w' },
      {   'id'          : 'base_currency_code',
          'type'        : 'string',
          'mode'        : 'w' },
      {   'id'          : 'destination',
          'type'        : 'string',
          'mode'        : 'w' },
      {   'id'          : 'destination_administration',
          'type'        : 'string',
          'mode'        : 'w' },
      {   'id'          : 'destination_decision',
          'type'        : 'string',
          'mode'        : 'w' },
      {   'id'          : 'destination_ownership',
          'type'        : 'string',
          'mode'        : 'w' },
      {   'id'          : 'payment_mode',
          'type'        : 'string',
          'mode'        : 'w' },
      {   'id' : 'costumer_id',
          'type' : 'string',
          'mode' : 'w' },
      {   'id' : 'delivery_addr_firstname',
          'type' : 'string',
          'mode' : 'w' },
      {   'id' : 'delivery_addr_lastname',
          'type' : 'string',
          'mode' : 'w' },
      {   'id' : 'delivery_addr_street',
          'type' : 'string',
          'mode' : 'w' },
      {   'id' : 'delivery_addr_city',
          'type' : 'string',
          'mode' : 'w' },
      {   'id' : 'delivery_addr_postcode',
          'type' : 'string',
          'mode' : 'w' },
      {   'id' : 'delivery_addr_country',
          'type' : 'string',
          'mode' : 'w' },
  )
