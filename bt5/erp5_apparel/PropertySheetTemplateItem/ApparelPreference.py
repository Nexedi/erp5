##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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

class ApparelPreference:
  """
    User Preferences for erp5_apparel.

    Contains all preferences (see portal_preferences) relative to apparel.
  """

  _properties = (
    { 'id'          : 'preferred_apparel_cloth_variation_base_category',
      'description' : 'Defines base categories axes in apparel cloth variations',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_apparel_shape_variation_base_category',
      'description' : 'Defines base categories axes in apparel shape variations',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_apparel_model_variation_base_category',
      'description' : 'Defines base categories axes in apparel model variations',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_apparel_fabric_variation_base_category',
      'description' : 'Defines base categories axes in apparel fabric variations',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_apparel_component_variation_base_category',
      'description' : 'Defines base categories axes in apparel conponent variations',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'write_permission': 'Manage properties',
      'mode'        : '' },
  )
