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

class Domain:
    """
        A Domain holds a list of variable properties which the domains
        applies to.
    """

    _properties = (
        # Optional reporting methods to extend predicate
        {   'id'          : 'select_method_id',
            'description' : 'A method (python, SQL) to select objects which satisfy the predicate',
            'type'        : 'string',
            'mode'        : 'w' },                
        {   'id'          : 'stat_method_id',
            'description' : 'A method (python, SQL) to calculate statistics on selected objects',
            'type'        : 'string',
            'mode'        : 'w' },                        
        # Legacy - now same with predicate    
        {   'id'          : 'domain_base_category',
            'storage_id'  : 'domain_base_category_list', # Compatibility
            'description' : 'The acceptable range of discrete variation',
            'type'        : 'tokens',
            'default'     : [],
            'mode'        : 'w' },
        {   'id'          : 'domain_property',
            'storage_id'  : 'domain_property_list', # Compatibility
            'description' : 'The domain properties for continuous variation range definition',
            'type'        : 'tokens',
            'default'     : [],
            'mode'        : 'w' },
    )

