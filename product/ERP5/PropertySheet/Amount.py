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

class Amount:
  """
        Properties for Amount. Amounts are a quantity
        of a given resource in a given  variation.

        The variation is stored in the category and properties

        Efficiency may need to be renamed - this
        is a proba value / fuzzy value

        variation is a reserverd name implemented as getVariation and setVariation....
        in the amount class
  """

  _properties = (
    { 'id'          : 'resource_id',
      'description' : "The resource id involved",
      'type'        : 'string',
      'acquisition_base_category' : ('resource',),
      'acquisition_portal_type'   : Expression('python: portal.getPortalResourceTypeList()'),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_sync_value'    : 0,
      'acquisition_accessor_id'   : 'getId',
      'acquisition_depends'       : None,
      'alt_accessor_id'           : ('_categoryGetResourceId', ),
      'mode'        : 'w' },
    { 'id'          : 'resource_relative_url',
      'description' : "The resource relative url involved",
      'type'        : 'string',
      'acquisition_base_category' : ('resource',),
      'acquisition_portal_type'   : Expression('python: portal.getPortalResourceTypeList()'),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_sync_value'    : 0,
      'acquisition_accessor_id'   : 'getRelativeUrl',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'resource_title',
      'description' : "The resource title involved",
      'type'        : 'string',
      'acquisition_base_category' : ('resource',),
      'acquisition_portal_type'   : Expression('python: portal.getPortalResourceTypeList()'),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_sync_value'    : 0,
      'acquisition_accessor_id'   : 'getTitle',
      'acquisition_depends'       : None,
      'alt_accessor_id'           : ('_categoryGetResourceTitle', ),
      'mode'        : 'w' },
    # Accounting
    { 'id'          : 'quantity',
      'description' : """The quantity of resource.""",
      'type'        : 'float',
      'default'     : 0.0,
      'acquisition_base_category'     : ('delivery',),
      'acquisition_portal_type'       : Expression('python: portal.getPortalAcquisitionMovementTypeList() + portal.getPortalDeliveryTypeList()'),
      'acquisition_copy_value'        : 0,
      'acquisition_mask_value'        : 1,
      'acquisition_accessor_id'       : 'getQuantity',
      'acquisition_depends'           : None,
      'alt_accessor_id'               : ('getTargetQuantity', ),
      'mode'        : 'w' },
    { 'id'          : 'efficiency',
      'description' : """The efficiency.""",
      'type'        : 'float',
      'default'     : 1.0,
      'acquisition_base_category'     : ('delivery',),
      'acquisition_portal_type'       : Expression('python: portal.getPortalAcquisitionMovementTypeList() + portal.getPortalDeliveryTypeList()'),
      'acquisition_copy_value'        : 0,
      'acquisition_mask_value'        : 1,
      'acquisition_accessor_id'       : 'getEfficiency',
      'acquisition_depends'           : None,
      'alt_accessor_id'               : ('getTargetEfficiency', ),
      'mode'        : 'w' },
    # Planning
    { 'id'          : 'target_quantity',
      'description' : """The target quantity of resource.""",
      'type'        : 'float',
      'default'     : 0.0,
      'acquisition_base_category'     : ('order',),
      'acquisition_portal_type'       : Expression('python: portal.getPortalAcquisitionMovementTypeList() + portal.getPortalOrderTypeList()'),
      'acquisition_copy_value'        : 0,
      'acquisition_mask_value'        : 1,
      'acquisition_accessor_id'       : 'getTargetQuantity',
      'acquisition_depends'           : None,
      'mode'        : 'w' },
    { 'id'          : 'target_efficiency',
      'description' : """The target efficiency.""",
      'type'        : 'float',
      'default'     : 1.0,
      'acquisition_base_category'     : ('order',),
      'acquisition_portal_type'       : Expression('python: portal.getPortalAcquisitionMovementTypeList() + portal.getPortalOrderTypeList()'),
      'acquisition_copy_value'        : 0,
      'acquisition_mask_value'        : 1,
      'acquisition_accessor_id'       : 'getTargetEfficiency',
      'acquisition_depends'           : None,
      'mode'        : 'w' },
    # Profit and loss
    { 'id'          : 'profit_quantity',
      'description' : 'A quantity which represents generation of resource from nowhere',
      'type'        : 'float',
      'default'     : 0.0,
      'mode'        : 'w' },
 )

  _categories = ('resource', 'quantity_unit')
