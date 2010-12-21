##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Leonardo Rochael Almeida <leonardo@nexedi.com>
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

from Products.ZMySQLDA.DA import Connection
from Products.ERP5Type.Globals import InitializeClass
from App.special_dtml import HTMLFile

# If the sort order below doesn't work, we cannot guarantee the setSortKey()
# call below will actually result in the activity connection being committed
# after the ZODB and Catalog data.
assert None < 0 < '' < (), "Cannot guarantee commit of activities comes after the appropriate data"

manage_addActivityConnectionForm = HTMLFile('dtml/connectionAdd', globals())

def manage_addActivityConnection(self, id, title,
                                 connection_string,
                                 check=None, REQUEST=None):
    """Add a DB connection to a folder"""
    self._setObject(id, Connection(id, title, connection_string, check))
    if REQUEST is not None: return self.manage_main(self,REQUEST)

class ActivityConnection(Connection):
    """Products ZMySQLDA.DA.Connection subclass that tweaks the sortKey() of
       the actual connection to commit after all other connections
    """
    meta_type = title = 'CMFActivity Database Connection'

    # Declarative constructors
    constructors = (manage_addActivityConnectionForm,
                    manage_addActivityConnection)

    # reuse the permission from ZMySQLDA
    permission_type = 'Add Z MySQL Database Connections'

    def connect(self, s):
        result = Connection.connect(self, s)
        # the call above will set self._v_database_connection, and it won't
        # have disappeared by now.
        # We need to put back this code as soon as problems are solved XXX
        #self._v_database_connection.setSortKey( (0,) )
        return result

InitializeClass(ActivityConnection)
