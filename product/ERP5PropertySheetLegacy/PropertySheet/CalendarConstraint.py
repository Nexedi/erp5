##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael M. Monnerat <rafael@nexedi.com>
#                    Jerome Perrin <jerome@nexedi.com>
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

class CalendarConstraint:
  """Constraints for Calendar
  """

  _constraints = (
    { 'id'            : 'presence_request_line',
      'type'          : 'ContentExistence',
      'portal_type'   : ('Presence Request Period', ),
      'description'   : 'No Presence Request Period created yet',
      'message_no_subobject_portal_type': 'No Presence Request Period created yet',
      'condition' :   'python: object.getPortalType() == "Presence Request"',
    },
    { 'id'            : 'leave_request_line',
      'type'          : 'ContentExistence',
      'portal_type'   : ('Leave Request Period', ),
      'description'   : 'No Leave Request Period created yet',
      'message_no_subobject_portal_type': 'No Leave Request Period created yet',
      'condition' :   'python: object.getPortalType() == "Leave Request"',
    },
    { 'id'            : 'group_request_line',
      'type'          : 'ContentExistence',
      'portal_type'   : ('Group Leave Period', 'Group Presence Period', ),
      'description'   : 'No Calendar Line created yet',
      'message_no_subobject_portal_type': 'No Calendar Line created yet',
      'condition' :   'python: object.getPortalType() == "Group Calendar"',
    },

 )
