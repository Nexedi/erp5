##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

class AcquiredProperty:
    """
    Define an Acquired Property for new-style Property Sheets
    """
    _properties = (
        {   'id': 'acquisition_base_category',
            'type': 'lines',
            'description' : 'The base categories to browse' },
        {   'id': 'acquisition_object_id',
            'type': 'lines',
            'description' : 'The default contained object id to look up' },
        # TALES expression
        {   'id': 'acquisition_portal_type',
            'type': 'string',
            'description' : 'The portal types to browse' },
        {   'id': 'acquisition_accessor_id',
            'type': 'string',
            'description' : 'Property to get from source' },
        {   'id': 'alt_accessor_id',
            'type': 'lines',
            'description' : 'Alternative accessor ids' },
        {   'id': 'acquisition_copy_value',
            'type': 'boolean',
            'description' : 'Determines if acquired value should be copied' },
        {   'id': 'acquisition_mask_value',
            'type': 'boolean',
            'description' : 'Determines if the local value have priority' },
        # TALES expression
        {   'id': 'content_portal_type',
            'type': 'string',
            'description' : 'Portal type of the object to create' },
        {   'id': 'content_acquired_property_id',
            'type': 'lines',
            'description' : 'Properties to be synchronized with the current object' },
        {   'id': 'content_translation_acquired_property_id',
            'type': 'lines',
            'description' : 'Properties to be translated' },
        )
