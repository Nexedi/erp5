##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

# This has to be chanegd and improved by the new category acquisition tool
from Products.CMFCore.Expression import Expression

class InventoryMovement:
  """
        Properties for InventoryMovement.

        No default value is set in order to allow
        None inventory values in movements

  """

  _properties = (

    # Inventory
    { 'id'          : 'inventory',
      'description' : """The quantity of items in stock after inventory.""",
      'type'        : 'float',
      'acquisition_base_category'     : ('delivery',),
      'acquisition_portal_type'       : Expression('python: portal.getPortalAcquisitionMovementTypeList() + portal.getPortalDeliveryTypeList()'),
      'acquisition_copy_value'        : 0,
      'acquisition_mask_value'        : 1,
      'acquisition_accessor_id'       : 'getInventory',
      'acquisition_depends'           : None,
      'mode'        : 'w' },
    { 'id'          : 'inventory_efficiency',
      'description' : """The efficiency of the inventory. 1.0 is perfect.""",
      'type'        : 'float',
      'default'     : None,
      'mode'        : 'w' },
  )

  _categories = ()
