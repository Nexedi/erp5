##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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

from Products.ERP5.ERP5Globals import *

class Movement:
    """
        Properties which allow to define a generic Movement.

        Movement always relate to an order which defines
        contractual information.
    """

    _properties = (
        # Accounting
        #{   'id'          : 'accountable',
        #    'description' : 'If set to 1, self must be accounted',
        #    'type'        : 'boolean',
        #    'default'     : 0,
        #    'mode'        : 'w' },
        # Order reference
        {   'id'          : 'order_title',
            'description' : 'The title of the order which defines contractual conditions',
            'type'        : 'string',
            'acquisition_base_category'     : ('order',),
            'acquisition_portal_type'       : order_type_list,
            'acquisition_copy_value'        : 0,
            'acquisition_accessor_id'       : 'getTitle',
            'acquisition_depends'           : None,
            'alt_accessor_id'               : ('_categoryGetOrderTitle', ),
            'mode'        : 'w' },
        {   'id'          : 'order_id',
            'description' : 'The id of the order which defines contractual conditions',
            'type'        : 'string',
            'acquisition_base_category'     : ('order',),
            'acquisition_portal_type'       : order_type_list,
            'acquisition_copy_value'        : 0,
            'acquisition_accessor_id'       : 'getId',
            'acquisition_depends'           : None,
            'alt_accessor_id'               : ('_categoryGetOrderId', ),
            'mode'        : 'w' },
        {   'id'          : 'order_relative_url',
            'description' : 'The relative_url of the order which defines contractual conditions',
            'type'        : 'string',
            'acquisition_base_category'     : ('order',),
            'acquisition_portal_type'       : order_type_list,
            'acquisition_copy_value'        : 0,
            'acquisition_accessor_id'       : 'getRelativeUrl',
            'acquisition_depends'           : None,
            'alt_accessor_id'               : ('_categoryGetOrderRelativeUrl', ),
            'mode'        : 'w' },
    )

    _categories = tuple(['order'] + list(variation_base_category_list))
                   # XXX Please check if it is meaningful to add order cat to all movemements ?
