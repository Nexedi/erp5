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

class CategoryMembershipArityConstraint:
    """
    Define a Category Membership Arity Constraint for ZODB Property Sheets
    """
    _properties = (
        {   'id': 'min_arity',
            'type': 'int',
            'description' : 'Minimum arity' },
        {   'id': 'max_arity',
            'type': 'int',
            'description' : 'Maximum arity' },
        {   'id': 'constraint_portal_type',
            'type': 'lines',
            'description' : 'Portal types',
            'default': () },
        {   'id': 'constraint_base_category',
            'type': 'lines',
            'description' : 'Base categories',
            'default': () },
        {   'id': 'message_arity_too_small',
            'type': 'string',
            'description' : 'Error message when the arity for the relation '\
                            'is too small',
            'default': 'Arity Error for Relation ${base_category}, arity is '\
                       'equal to ${current_arity} but should be at least '\
                       '${min_arity}' },
        {   'id': 'message_arity_not_in_range',
            'type': 'string',
            'description' : 'Error message when the arity for the relation '\
                            'is out of bounds',
            'default': 'Arity Error for Relation ${base_category}, arity is '\
                       'equal to ${current_arity} but should be between '\
                       '${min_arity} and ${max_arity}' },
        {   'id': 'message_arity_with_portal_type_too_small',
            'type': 'string',
            'description' : 'Error message when the arity for the relation '\
                            'and portal type is too small',
            'default': 'Arity Error for Relation ${base_category} and Type '\
                       '${portal_type}, arity is equal to ${current_arity} '\
                       'but should be at least ${min_arity}' },
        {   'id': 'message_arity_with_portal_type_not_in_range',
            'type': 'string',
            'description' : 'Error message when the arity for the relation '\
                            'and portal type is out of bounds',
            'default': 'Arity Error for Relation ${base_category} and Type '\
                       '${portal_type}, arity is equal to ${current_arity} '\
                       'but should be between ${min_arity} and ${max_arity}' },
        )
