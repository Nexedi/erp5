# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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

"""
SQL (MySQL) based cache plugin.
"""

from thread import get_ident
import time
import base64
from zLOG import LOG
from BaseCache import BaseCache, CacheEntry, CachedMethodError
from Products.ERP5Type import Interface
import zope.interface

try:
  import cPickle as pickle
except ImportError:
  import pickle
    
try:
  import MySQLdb
  from MySQLdb.constants import CR
  from _mysql_exceptions import OperationalError
  hosed_connection = (
      CR.SERVER_GONE_ERROR,
      CR.SERVER_LOST
      )
except ImportError:
  LOG('SQLCache', 0, 'unable to import MySQLdb')

  
## global ditionary containing connection objects
connection_pool = {}
  
class SQLCache(BaseCache):
  """ SQL based cache plugin. """

  zope.interface.implements(
        Interface.ICachePlugin
    )

  cache_expire_check_interval = 3600
    
  create_table_sql = '''CREATE TABLE %s(cache_id VARBINARY(970) NOT NULL, 
                                         value LONGTEXT,
                                         scope VARBINARY(20),
                                         stored_at INT,
                                         cache_duration INT DEFAULT 0,
                                         calculation_time FLOAT,
                                         UNIQUE(cache_id, scope))
                      '''

  insert_key_sql = '''REPLACE INTO %s (cache_id, value, scope, stored_at, cache_duration, calculation_time) 
                              VALUES("%s", "%s", "%s", %s, %s, %s)
                    '''
                            
  has_key_sql = '''SELECT count(*)
                    FROM %s
                    WHERE cache_id = "%s" and scope="%s"
                    '''
                      
  get_key_sql = '''SELECT value, cache_duration, calculation_time 
                    FROM %s
                    WHERE cache_id = "%s" and scope="%s"
                    '''
                            
  delete_key_sql = '''DELETE
                       FROM %s
                       WHERE cache_id = "%s" and scope="%s"
                    '''
    
  delete_all_keys_sql = '''DELETE 
                            FROM %s
                         '''
    
  delete_all_keys_for_scope_sql = '''DELETE 
                                      FROM %s 
                                      WHERE scope="%s"
                                    '''
        
  delete_expired_keys_sql = '''DELETE 
                                FROM %s
                                WHERE cache_duration + stored_at < %s and cache_duration!=0
                              '''
  
  get_scope_list_sql = '''SELECT scope 
                           FROM %s 
                           GROUP BY scope
                        '''
                           
  get_scope_key_list_sql = '''SELECT cache_id 
                                FROM %s 
                                WHERE scope="%s"
                            '''
                            
  find_table_by_name_sql = """SHOW TABLES LIKE '%s' """
  
  def __init__(self, params={}):
    BaseCache.__init__(self)
    self._dbConn = None
    self._db_server = params.get('server', '')
    self._db_user = params.get('user', '')
    self._db_passwd = params.get('passwd', '')
    self._db_name = params.get('db', '')
    self._db_cache_table_name = params.get('cache_table_name')
    
    ## since SQL cache is persistent check for expired objects
    #self.expireOldCacheEntries(forceCheck=True)
  
  def initCacheStorage(self):
    """ Init cache backedn storage by creating needed cache table in RDBMS """
    sql_query = self.find_table_by_name_sql %self._db_cache_table_name
    cursor =  self.execSQLQuery(sql_query)
    result = cursor.fetchall()
    if 0 < len(result):
      ## we have such table
      pass
    else:
      ## no such table create it
      self.execSQLQuery(self.create_table_sql %self._db_cache_table_name) 
  
  def getCacheStorage(self, **kw):
    """ 
    Return current DB connection or create a new one for this thread.
    See http://sourceforge.net/docman/display_doc.php?docid=32071&group_id=22307
    especially threadsafety part why we create for every thread a new MySQL db connection object.
    """
    force_reconnect = kw.get('force_reconnect', False)
    global connection_pool
    thread_id = get_ident()
    
    dbConn = connection_pool.get(thread_id, None)
    if force_reconnect or dbConn is None:
      ## we don't have dbConn for this thread
      dbConn = MySQLdb.connect(host=self._db_server, \
                               user=self._db_user,\
                               passwd=self._db_passwd, \
                               db=self._db_name)
      connection_pool[thread_id] = dbConn
      return dbConn      
    else:
      ## we have already dbConn for this thread 
      return dbConn
    
  def get(self, cache_id, scope, default=None):
    sql_query = self.get_key_sql %(self._db_cache_table_name, cache_id, scope)
    cursor =  self.execSQLQuery(sql_query)
    if cursor:
      ## count return one row only
      result = cursor.fetchall()
      if 0 < len(result):
        ## we found results
        result = result[0]
        decoded_result = pickle.loads(base64.decodestring(result[0]))
        #self.markCacheHit()
        cache_entry = CacheEntry(decoded_result, result[1], result[2])
        return cache_entry
      else:
        ## no such cache_id in DB
        return None
    else:
      ## DB not available
      return None
        
  def set(self, cache_id, scope, value, cache_duration=None, calculation_time=0):
    value = base64.encodestring(pickle.dumps(value,2))
    if not cache_duration:
      ## should live forever ==> setting cache_duration = 0 will make it live forever
      cache_duration = 0
    else:
      ## we have strict cache_duration defined. we calculate seconds since start of epoch
      cache_duration = int(cache_duration)
    ## Set key in DB
    stored_at = int(time.time())
    sql_query = self.insert_key_sql %(self._db_cache_table_name, cache_id, value, scope, stored_at, cache_duration, calculation_time)
    self.execSQLQuery(sql_query)
    #self.markCacheMiss()
            
  def expireOldCacheEntries(self, forceCheck = False):
    now = time.time()
    if forceCheck or (now > self._next_cache_expire_check_at):
      ## time to check for expired cache items
      self._next_cache_expire_check_at = now + self.cache_expire_check_interval
      my_query = self.delete_expired_keys_sql %(self._db_cache_table_name, now)
      self.execSQLQuery(my_query)

  def delete(self, cache_id, scope):
    my_query = self.delete_key_sql %(self._db_cache_table_name, cache_id, scope)
    self.execSQLQuery(my_query)
    
  def has_key(self, cache_id, scope):
    my_query = self.has_key_sql %(self._db_cache_table_name, cache_id, scope)
    cursor =  self.execSQLQuery(my_query)
    if cursor:
      ## count() SQL function will return one row only
      result = cursor.fetchall()
      result = result[0][0] 
      if result == 0:
        ## no such key in DB
        return False
      elif result==1:
        ## we have this key in DB
        return True
      else:
        ## something wrong in DB model
        raise CachedMethodError, "Invalid cache table reltion format. cache_id MUST be unique!"
    else:
      ## DB not available
      return False

  def getScopeList(self):
    rl = []
    my_query = self.get_scope_list_sql %(self._db_cache_table_name)
    cursor =  self.execSQLQuery(my_query)
    results = cursor.fetchall() 
    for result in results:
        rl.append(result[0])
    return rl
    
  def getScopeKeyList(self, scope):
    rl = []
    my_query = self.get_scope_key_list_sql %(self._db_cache_table_name, scope)
    cursor =  self.execSQLQuery(my_query)
    results = cursor.fetchall() 
    for result in results:
        rl.append(result[0])
    return rl
    
  def clearCache(self):
    BaseCache.clearCache(self)
    ## SQL Cache is a persistent storage rather than delete all entries
    ## just expire them 
    ## self.expireOldCacheEntries(forceCheck = True):
    my_query = self.delete_all_keys_sql  %(self._db_cache_table_name)
    self.execSQLQuery(my_query)
    
  def clearCacheForScope(self, scope):
    my_query = self.delete_all_keys_for_scope_sql  %(self._db_cache_table_name, scope)
    self.execSQLQuery(my_query)

  def _execSQLQuery(self, sql_query, connection):
    """
      Execute sql query using given connection.
    """
    cursor = connection.cursor()
    cursor.execute(sql_query)
    return cursor

  def execSQLQuery(self, sql_query):
    """ 
    Try to execute sql query.
    Return cursor object because some queris can return result
    """
    dbConn = self.getCacheStorage()
    try:
      cursor = self._execSQLQuery(sql_query, dbConn)
    except OperationalError, m:
      if m[0] not in hosed_connection:
        raise
      dbConn = self.getCacheStorage(force_reconnect=True)
      cursor = self._execSQLQuery(sql_query, dbConn)
    return cursor

  def getCachePluginTotalMemorySize(self):
    """ Calculate total RAM memory size of cache plugin. """
    return 0       
