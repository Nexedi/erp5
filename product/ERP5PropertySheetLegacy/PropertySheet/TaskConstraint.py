##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                          Rafael Monnerat <rafael@nexedi.com>
#                           
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

class TaskConstraint:
  """
     Constraintsts For Task
  """
      
  _constraints = (
    { 'id'            : 'source_category_membership_arity',
      'description'   : 'Source must be defined',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '1',
      'max_arity'     : '1',
      'portal_type'   : ('Person', 'Organisation', 'Category'),
      'base_category' : ('source',),
      'message_arity_with_portal_type_not_in_range': 'Assignee must be defined',
    },
    { 'id'            : 'destination_category_membership_arity',
      'description'   : 'Destination must be defined',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '1',
      'max_arity'     : '1',
      'portal_type'   : ('Person', 'Organisation', 'Category'),
      'base_category' : ('destination',),
      'message_arity_with_portal_type_not_in_range': 'Location must be defined',
    },
    { 'id'            : 'start_date_existence',
      'description'   : 'Property start_date must be defined',
      'type'          : 'PropertyExistence',
      'start_date'    : None,
      'message_property_not_set': 'Begin Date must be defined',
      'message_no_such_property' : 'Begin Date must be defined' 
    },
    { 'id'            : 'date_coherency',
      'description'   : 'Stop Date must be after Start Date',
      'type'          : 'TALESConstraint',
      'expression'    : 'python: object.getStopDate() >= object.getStartDate()',
      'message_expression_false': 'End Date must be after Begin Date',
    },
    { 'id'            : 'lines',
      'description'   : 'Lines must be defined',
      'type'          : 'ContentExistence',
      'portal_type'   : ('Task Line', 'Task Report Line' ),
      'message_no_subobject_portal_type' : \
                                'At least one line is required',
    },
  )
