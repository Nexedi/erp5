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

class Login:
    """
        Properties for Login (user ID, password, and some day
        more properties such as X509 certificates).

        Login information used to be defined on the Person
        propertysheet. However, such Login information is
        more general and needs to be defined on different objects
        such as External Sources (ex. IMAP Reader).
 
        TODO:
        - add acquisition from reference property for used_id
          to prepare transition
    """

    _properties = (
        {   'id'            : 'password'
          , 'description'   : 'The password required to login'
          , 'type'          : 'string'
          , 'write_permission' : 'Set own password'
          , 'read_permission'  : 'Manage users'
          , 'mode'          : 'w'
        },
        {   'id'            : 'user_id'
          , 'description'   : 'The user ID required to login'
          , 'type'          : 'string' # XXX Possibly add acquisition from reference property
          , 'mode'          : 'rw'
        },
     )
