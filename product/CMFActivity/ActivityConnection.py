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

from Products.ZMySQLDA.DA import Connection, DB
from Products.ERP5Type.Globals import InitializeClass
from App.special_dtml import HTMLFile
from Acquisition import aq_parent

# If the sort order below doesn't work, we cannot guarantee the sort key
# used below will actually result in the activity connection being committed
# after the ZODB and Catalog data.
assert '\x00' < '-1' < '0' < '1' < '\xff', "Cannot guarantee commit of activities comes after the appropriate data"

manage_addActivityConnectionForm = HTMLFile('dtml/connectionAdd', globals())

def manage_addActivityConnection(self, id, title,
                                 connection_string,
                                 check=None, REQUEST=None):
    """Add a DB connection to a folder"""
    self._setObject(id, ActivityConnection(id, title, connection_string, check))
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

    def factory(self):
        return ActivityDB

InitializeClass(ActivityConnection)


class ActivityDB(DB):

    _sort_key = '\xff'
