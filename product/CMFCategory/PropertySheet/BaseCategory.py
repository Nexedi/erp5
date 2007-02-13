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

class BaseCategory:
    """
        Properties for BaseCategory Objects
    """

    _properties = (
        {   'id'          : 'acquisition_object_id',
            'description' : 'The default contained object id to look up',
            'type'        : 'lines',
            'default'     : [],
            'mode'        : 'w' },
        {   'id'          : 'acquisition_base_category',
            'description' : 'The base categories to browse',
            'type'        : 'tokens',
            'default'     : [],
            'mode'        : 'w' },
        {   'id'          : 'acquisition_portal_type',
            'description' : 'The portal types to browse',
            'type'        : 'tales',
            'default'     : 'python:[]',
            'multivalued' : 1,
            'mode'        : 'w' },
        {   'id'          : 'fallback_base_category',
            'description' : 'another base category to get if everything else fails',
            'type'        : 'tokens',
            'default'     : [],
            'mode'        : 'w' },
        {   'id'          : 'acquisition_copy_value',
            'description' : 'Determines if acquired value should be copied',
            'type'        : 'boolean',
            'default'     : 0,
            'mode'        : 'w' },
        {   'id'          : 'acquisition_mask_value',
            'description' : 'Determines if the local value have priority',
            'type'        : 'boolean',
            'default'     : 1,
            'mode'        : 'w' },
        {   'id'          : 'acquisition_append_value',
            'description' : 'Determines if the acquired value should be appended',
            'type'        : 'boolean',
            'default'     : 0,
            'mode'        : 'w' },
        {   'id'          : 'acquisition_sync_value',
            'description' : 'Determines if the acquired value should be synced',
            'type'        : 'boolean',
            'default'     : 0,
            'mode'        : 'w' },
        {   'id'          : 'read_permission',
            'description' : 'permission needed to access Getters',
            'type'        : 'string',
            'default'     : None,
            'mode'        : 'w' },
        {   'id'          : 'write_permission',
            'description' : 'permission needed to access Setters',
            'type'        : 'string',
            'default'     : None,
            'mode'        : 'w' },
        {   'id'          : 'category_type',
            'description' : 'Category types to group categories for portal methods',
            'type'        : 'lines',
            'default'     : [],
            'mode'        : 'w' },
    )


