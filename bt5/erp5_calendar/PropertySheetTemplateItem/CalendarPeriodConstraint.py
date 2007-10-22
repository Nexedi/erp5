##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Rafael M. Monnerat <rafael@nexedi.com>
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

class CalendarPeriodConstraint:
    """
     Calendar Period Constraints
    """
    _constraints = (
      {   'id'            : 'start_date_existence',
          'description'   : 'Property start_date must be defined',
          'type'          : 'PropertyExistence',
          'start_date'    : None,
      },
      {   'id'            : 'stop_date_existence',
          'description'   : 'Property stop date must be defined',
          'type'          : 'PropertyExistence',
          'stop_date'    : None,
      },
      { 'id'            : 'resource',
        'description'   : 'Type must be defined',
        'type'          : 'CategoryMembershipArity',
        'min_arity'     : '1',
        'max_arity'     : '1',
        'portal_type'   : ('Category', ),
        'base_category' : ('resource',)
      },
    )
