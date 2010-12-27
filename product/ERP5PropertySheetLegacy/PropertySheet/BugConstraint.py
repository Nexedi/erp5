##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#                     Rafael Monnerat <rafael@nexedi.com>
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

class BugConstraint:
  """
     Constraintsts For Bug Objects
  """
      
  _constraints = (
    { 'id'            : 'title_existence',
      'description'   : 'Title must be defined',
      'type'          : 'PropertyExistence',
      'title'         :  None,
      'message_no_such_property' : 'Title must be defined',
    },
    { 'id'            : 'tested_existence',
      'description'   : 'Tested must be defined',
      'type'          : 'PropertyExistence',
      'tested'        :  0,
      'condition'     : "python: object.getSimulationState() in ['ready','stopped']" ,
      'message_no_such_property' : 'Tested is unchecked, Must have a Unit/Funcional test for this',
    },
    { 'id'            : 'source_project_category_membership_arity',
     'description'   : 'Handler Project must be defined',
     'type'          : 'CategoryMembershipArity',
     'min_arity'     : '1',
     'max_arity'     : '1',
     'portal_type'   : ('Project', 'Project Line' ),
     'base_category' : ('source_project',),
     'message_arity_with_portal_type_not_in_range': 'Handler Project must be defined',
    },
    { 'id'            : 'start_date_existence',
      'description'   : 'Property start_date must be defined',
      'type'          : 'PropertyExistence',
      'start_date'    : None,
      'message_no_such_property' : 'Begin Date must be defined' 
    },
    { 'id'            : 'date_coherency',
      'description'   : 'Stop Date must be after Start Date',
      'type'          : 'TALESConstraint',
      'expression'    : 'python: object.getStopDate() >= object.getStartDate()',
      'message_expression_false': 'End Date must be after Begin Date',
    },
  )
