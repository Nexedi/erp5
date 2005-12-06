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

class Reference:
    """
        Properties which define the references of a document
    """

    _properties = (
        # Sourcing / planning properties
        {   'id'          : 'reference',
            'storage_id'  : 'default_reference', # Compatibility
            'description' : 'The absolute references of the document (our reference)',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'source_reference',
            'storage_id'  : 'default_source_reference', # Compatibility
            'description' : 'The references of the document for default sources',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'destination_reference',
            'storage_id'  : 'default_destination_reference', # Compatibility
            'description' : 'The references of the document for default destinations',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'grouping_reference',
            'description' : 'A reference which allows to unify multiple objects',
            'type'        : 'string',
            'mode'        : 'w' },
        # Do not use the property below - it may be replaced by calculated
        # references made out of reference, version_reference, portal_type, etc.
        # ex. PROD-33456724-3
        {   'id'          : 'document_reference', # XXX ERROR - we already have a reference
            'description' : 'The references of the document itself',
            'type'        : 'string',
            'mode'        : 'w' },
    )

    _categories = ()

