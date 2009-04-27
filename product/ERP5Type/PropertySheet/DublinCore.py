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



class DublinCore:
    """
        Properties of DublinCore
    """

    _properties = (
        {   'id'          : 'title',
            'description' : '',
            'type'        : 'string',
            'translatable'  : 1,
            'translation_domain' : 'erp5_content',
            'default'     : '',
            'acquisition_base_category': (),
            'acquisition_portal_type': (),
            'acquisition_copy_value': 0,
            'acquisition_mask_value': 1,
            'acquisition_accessor_id': 'getTitle',
            'acquisition_depends': None,
            'alt_accessor_id': ('getCompactTitle',),
            'mode'        : 'w' },
        {   'id'          : 'subject',
            'description' : '',
            'type'        : 'lines',
            'default'     : (),
            'mode'        : 'w' },
        {   'id'          : 'description',
            'description' : '',
            'default'     : '',
            'type'        : 'text',
            'mode'        : 'w' },
        {   'id'          : 'contributor',
            'storage_id'  : 'contributors', # CMF Compatibility
            'description' : '',
            'type'        : 'lines',
            'default'     : (),
            'mode'        : 'w' },
        {   'id'          : 'effective_date',
            'description' : '',
            'type'        : 'date',
            'mode'        : 'w' },
        {   'id'          : 'expiration_date',
            'description' : '',
            'type'        : 'date',
            'mode'        : 'w' },
        {   'id'          : 'format',
            'description' : '',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'language',
            'description' : '',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'right',
            'storage_id'  : 'rights',  # CMF Compatibility
            'description' : '',
            'type'        : 'string',
            'mode'        : 'w' },
        # Extended properties specific to ERP5 - not part of DublinCore
        {   'id'          : 'short_title',
            'description' : '',
            'type'        : 'string',
            'default'     : '',
            'translatable'  : 1,
            'translation_domain' : 'erp5_content',
            'mode'        : 'w' },
    )

