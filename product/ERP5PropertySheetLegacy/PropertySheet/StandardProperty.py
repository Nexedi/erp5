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

from Products.ERP5Type import Permissions

class StandardProperty:
    """
    Define a Standard Property for ZODB Property Sheets
    """
    _properties = (
        # 'reference'  has  be  used  in  favor  of  'id'  because  of
        # UniqueObject forbidding 'title' ID for example
        {   'id': 'reference',
            'type': 'string',
            'description': 'Property name' },
        # TALES expression
        {   'id': 'property_default',
            'type': 'string',
            'description': 'Default value if not set',
            'default': None },
        {   'id': 'multivalued',
            'type': 'boolean',
            'description': 'Determines if the property is multivalued',
            'default': False },
        {   'id': 'range',
            'type': 'boolean',
            'description': 'Determines if the range accessors should be created' ,
            'default': False },
        {   'id': 'preference',
            'type': 'boolean',
            'description': 'Determines if the preference accessors should be created',
            'default': False },
        # CMF compatibility
        {   'id': 'storage_id',
            'type': 'string',
            'description' : 'Name to be used instead of the Reference',
            'default': None },
        {   'id': 'read_permission',
            'type': 'string',
            'description' : 'Permission needed to access Getters',
            'default': Permissions.AccessContentsInformation },
        {   'id': 'write_permission',
            'type': 'string',
            'description' : 'Permission needed to access Setters',
            'default': Permissions.ModifyPortalContent },
        )

    _categories = ('elementary_type',)
