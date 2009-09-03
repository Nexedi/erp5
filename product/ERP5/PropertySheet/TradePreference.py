#############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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


class TradePreference:
  """ This property sheet defines what can be configured on preferences for
  trade.
  """

  _properties = (
    # roles
    { 'id'          : 'preferred_client_role',
      'description' : 'Roles of clients',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_supplier_role',
      'description' : 'Roles of suppliers',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },

    # uses
    { 'id'          : 'preferred_sale_use',
      'description' : 'Uses of resources that are sold',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_purchase_use',
      'description' : 'Uses of resources that are purchased',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_packing_use',
      'description' : 'Uses of resources that are packing containers',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },

    )
