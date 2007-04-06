##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                     Vincent Pelletier <vincent@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from _mysql_exceptions import OperationalError
from Products.ZMySQLDA.db import hosed_connection
from thread import get_ident
from zLOG import LOG

UNCONNECTED_STATE = 0
CONNECTED_STATE = 1
GLOBAL_DB_CONNECTED_FLAG = UNCONNECTED_STATE

def fake_db_store_result(self, *args, **kw):
  """
    Mimic store_result to make sure it doesn't fail due to no executed queries.
  """
  return

def fake_connection_forceReconnection(self):
  """
    Intercept reconnection symptom.
  """
  global GLOBAL_DB_CONNECTED_FLAG
  GLOBAL_DB_CONNECTED_FLAG = CONNECTED_STATE
  return self.original_forceReconnection()

def fake_db_query(self, *args, **kw):
  """
    Mimic a failing query due to a disconnected socket from mysql server.
  """
  global GLOBAL_DB_CONNECTED_FLAG
  if GLOBAL_DB_CONNECTED_FLAG == UNCONNECTED_STATE:
    raise OperationalError, (hosed_connection[0], 'dummy exception')
  return self.original_query(*args, **kw)

class TestDeferredConnection(ERP5TypeTestCase):
  """
    Test MySQL Deferred Connection
  """

  def getBusinessTemplateList(self):
    return tuple()

  def getTitle(self):
    return "Deferred Connection"

  def setUp(self):
    ERP5TypeTestCase.setUp(self)

  def afterSetUp(self):
    self.login()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('vincent', '', ['Manager'], [])
    user = uf.getUserById('vincent').__of__(uf)
    newSecurityManager(None, user)

  def monkeypatchConnection(self, connection):
    """
      Apply monkey patch on db and reset connection state to "unconnected".
      Returns a tuple containing original functions.
    """
    mysql_class = connection.db.__class__
    mysql_class.original_query = mysql_class.query
    mysql_class.query = fake_db_query
    connection.__class__.original_forceReconnection = connection.__class__._forceReconnection
    connection.__class__._forceReconnection = fake_connection_forceReconnection
    GLOBAL_DB_CONNECTED_FLAG = UNCONNECTED_STATE

  def unmonkeypatchConnection(self, connection):
    """
      Revert monkeypatching done on db.
    """
    connection.__class__._forceReconnection = connection.__class__.original_forceReconnection
    delattr(connection.__class__, 'original_forceReconnection')
    mysql_class = connection.db.__class__
    mysql_class.query = mysql_class.original_query
    delattr(mysql_class, 'original_query')

  def getDeferredConnection(self):
    """
      Return site's deferred connection object.
    """
    deferred = self.getPortal().erp5_sql_deferred_connection
    deferred_connection = getattr(deferred, '_v_database_connection', None)
    if deferred_connection is None:
      deferred.connect(deferred.connection_string)
      deferred_connection = getattr(deferred, '_v_database_connection')
    deferred_connection.tables() # Dummy access to force actual connection.
    return deferred_connection._pool_get(get_ident())

  def test_00_basicReplaceQuery(self):
    """
      Check that a basic query succeeds.
    """
    connection = self.getDeferredConnection()
    connection.query('REPLACE INTO `full_text` SET `uid`=0, `SearchableText`="dummy test"')
    try:
      get_transaction().commit()
    except OperationalError:
      self.fail()
    except:
      raise # Make sure the test is known to have failed, even if it's not
            # the expected execution path.

  def test_01_disconnectsCausesError(self):
    """
      Check that a disconnection from mysql causes classical
      connection.db.query to fail.
      This makes sure that disconnection-trick monkey patch does work.
    """
    connection = self.getDeferredConnection()
    # Queue a query
    connection.query('REPLACE INTO `full_text` SET `uid`=0, `SearchableText`="dummy test"')
    # Replace dynamically the function used to send queries to mysql so it's
    # dumber than the implemented one.
    self.monkeypatchConnection(connection)
    connection._query = connection.db.query
    try:
      try:
        get_transaction().commit()
      except OperationalError, m:
        if m[0] not in hosed_connection:
          raise
      except:
        raise # Make sure the test is known to have failed, even if it's not
              # the expected execution path.
      else:
        self.fail()
    finally:
      delattr(connection, '_query')
      self.unmonkeypatchConnection(connection)

  def test_02_disconnectionRobustness(self):
    """
      Check that if the connection gets closed before being used the
      commit can happen without trouble.
    """
    connection = self.getDeferredConnection()
    # Queue a query
    connection.query('REPLACE INTO `full_text` SET `uid`=0, `SearchableText`="dummy test"')
    # Artificially cause a connection close.
    self.monkeypatchConnection(connection)
    try:
      try:
        get_transaction().commit()
      except OperationalError, m:
        LOG('TestDeferredConnection', 0, 'OperationalError exception raised: %s' % (m, ))
        self.fail()
      except:
        raise # Make sure the test is known to have failed, even if it's not
              # the expected execution path.
    finally:
      self.unmonkeypatchConnection(connection)

  def test_03_successiveTransactionsIsolation(self):
    """
      Check that multiple transactions (one after another) are correctly
      isolated one from the other.
    """
    connection = self.getDeferredConnection()
    # Queue a query
    connection.query('REPLACE INTO `full_text` SET `uid`=0, `SearchableText`="dummy test"')
    self.assertEqual(len(connection._sql_string_list), 1)
    get_transaction().commit()
    connection.query('REPLACE INTO `full_text` SET `uid`=0, `SearchableText`="dummy test"')
    self.assertEqual(len(connection._sql_string_list), 1)

if __name__ == '__main__':
  unittest.main()
