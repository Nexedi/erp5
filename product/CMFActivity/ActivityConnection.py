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

from App.special_dtml import HTMLFile
from Products.ERP5Type.Globals import InitializeClass
from Products.ZSQLDA.MySQL import Connection as MySQLConnection
from Products.ZSQLDA.MySQL import DB as MySQLDB
from Products.ZSQLDA.SQLite import Connection as SQLiteConnection
from Products.ZSQLDA.SQLite import DB as SQLiteDB

# If the sort order below doesn't work, we cannot guarantee the sort key
# used below will actually result in the activity connection being committed
# after the ZODB and Catalog data.
assert '' < chr(0) < chr(1) < 'xxx' < chr(255), "Cannot guarantee commit of activities comes after the appropriate data"


manage_addMySQLActivityConnectionForm = HTMLFile('dtml/connectionAdd_mysql', globals())

def manage_addMySQLActivityConnection(self, id, title,
                                      connection_string,
                                      check=None, REQUEST=None):
    """Add a MySQL CMFActivity DB connection to a folder"""
    connection = MySQLActivityConnection(id, title, connection_string)
    self._setObject(id, connection)
    if check:
        connection.connect(connection_string)
    if REQUEST is not None: return self.manage_main(self, REQUEST)


manage_addSQLiteActivityConnectionForm = HTMLFile('dtml/connectionAdd_sqlite', globals())

def manage_addSQLiteActivityConnection(self, id, title,
                                       connection_string,
                                       check=None, REQUEST=None):
    """Add a SQLite CMFActivity DB connection to a folder"""
    connection = SQLiteActivityConnection(id, title, connection_string)
    self._setObject(id, connection)
    if check:
        connection.connect(connection_string)
    if REQUEST is not None: return self.manage_main(self, REQUEST)


class MySQLActivityDB(MySQLDB):

    _sort_key = chr(255)

    @property
    def isolation_level(self):
        if not self.innodb_locks_unsafe_for_binlog:
            return 'READ COMMITTED'


class MySQLActivityConnection(MySQLConnection):
    """ZSQLDA MySQL Connection subclass that tweaks the sortKey() of the
       actual connection to commit after all other connections
    """
    meta_type = title = 'CMFActivity MySQL Database Connection'

    constructors = (manage_addMySQLActivityConnectionForm,
                    manage_addMySQLActivityConnection)

    permission_type = 'Add Z MySQL Database Connections'

    def factory(self):
        return MySQLActivityDB

InitializeClass(MySQLActivityConnection)


class SQLiteActivityDB(SQLiteDB):

    _sort_key = chr(255)


class SQLiteActivityConnection(SQLiteConnection):
    """ZSQLDA SQLite Connection subclass that tweaks the sortKey() of the
       actual connection to commit after all other connections
    """
    meta_type = title = 'CMFActivity SQLite Database Connection'

    constructors = (manage_addSQLiteActivityConnectionForm,
                    manage_addSQLiteActivityConnection)

    permission_type = 'Add Z SQLite Database Connections'

    def factory(self):
        return SQLiteActivityDB

InitializeClass(SQLiteActivityConnection)
