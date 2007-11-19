##############################################################################
#
# Copyright (c) 2002 Nexedi SARL. All Rights Reserved.
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Persistence import Persistent
import Acquisition
import ExtensionClass
import Globals
import OFS.History
from Globals import DTMLFile, PersistentMapping
from string import split, join
from thread import allocate_lock, get_ident
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from BTrees.OIBTree import OIBTree
from App.config import getConfiguration
from BTrees.Length import Length
from Shared.DC.ZRDB.TM import TM

from DateTime import DateTime
from Acquisition import aq_parent, aq_inner, aq_base
from zLOG import LOG, WARNING, INFO, TRACE
from ZODB.POSException import ConflictError
from DocumentTemplate.DT_Var import sql_quote
from Products.PythonScripts.Utility import allow_class

import time
import sys
import urllib
import string
import pprint
from cStringIO import StringIO
from xml.dom.minidom import parse
from xml.sax.saxutils import escape, quoteattr
import os
import md5

try:
  from Products.CMFCore.Expression import Expression
  from Products.PageTemplates.Expressions import getEngine
  from Products.CMFCore.utils import getToolByName
  withCMF = 1
except ImportError:
  withCMF = 0

try:
  import psyco
except ImportError:
  psyco = None

try:
  from Products.ERP5Type.Cache import enableReadOnlyTransactionCache
  from Products.ERP5Type.Cache import disableReadOnlyTransactionCache, CachingMethod
except ImportError:
  def doNothing(context):
    pass
  class CachingMethod:
    """
      Dummy CachingMethod class.
    """
    def __init__(self, callable, **kw):
      self.function = callable
    def __call__(self, *opts, **kw):
      return self.function(*opts, **kw)
  enableReadOnlyTransactionCache = doNothing
  disableReadOnlyTransactionCache = doNothing

UID_BUFFER_SIZE = 300
OBJECT_LIST_SIZE = 300
MAX_PATH_LEN = 255
RESERVED_KEY_LIST = ('where_expression', 'sort-on', 'sort_on', 'sort-order', 'sort_order', 'limit',
                     'format', 'search_mode', 'operator', 'selection_domain', 'selection_report')

valid_method_meta_type_list = ('Z SQL Method', 'LDIF Method', 'Script (Python)') # Nicer

full_text_search_modes = { 'natural': '',                                   # XXX-JPS probably not right place
                           'in_boolean_mode': 'IN BOOLEAN MODE',            # full_text_search_modes wrong naming
                           'with_query_expansion': 'WITH QUERY EXPANSION' } # according to ERP5 conventions
                                                                            # we really need a good grammar
                                                                            # and some cleanup

manage_addSQLCatalogForm = DTMLFile('dtml/addSQLCatalog',globals())

# Here go uid buffers
# Structure:
#  global_uid_buffer_dict[catalog_path][thread_id] = UidBuffer
global_uid_buffer_dict = {}

def manage_addSQLCatalog(self, id, title,
             vocab_id='create_default_catalog_', # vocab_id is a strange name - not abbreviation
             REQUEST=None):
  """Add a Catalog object
  """
  id = str(id)
  title = str(title)
  vocab_id = str(vocab_id)
  if vocab_id == 'create_default_catalog_':
    vocab_id = None

  c = Catalog(id, title, self)
  self._setObject(id, c)
  if REQUEST is not None:
    return self.manage_main(self, REQUEST,update_menu=1)

def isSimpleType(value):
  return isinstance(value, basestring) or \
         isinstance(value, int) or \
         isinstance(value, long) or \
         isinstance(value, float)


class UidBuffer(TM):
  """Uid Buffer class caches a list of reserved uids in a transaction-safe way."""

  def __init__(self):
    """Initialize some variables.

      temporary_buffer is used to hold reserved uids created by non-committed transactions.

      finished_buffer is used to hold reserved uids created by committed-transactions.

      This distinction is important, because uids by non-committed transactions might become
      invalid afterwards, so they may not be used by other transactions."""
    self.temporary_buffer = {}
    self.finished_buffer = []

  def _finish(self):
    """Move the uids in the temporary buffer to the finished buffer."""
    tid = get_ident()
    try:
      self.finished_buffer.extend(self.temporary_buffer[tid])
      del self.temporary_buffer[tid]
    except KeyError:
      pass

  def _abort(self):
    """Erase the uids in the temporary buffer."""
    tid = get_ident()
    try:
      del self.temporary_buffer[tid]
    except KeyError:
      pass

  def __len__(self):
    tid = get_ident()
    l = len(self.finished_buffer)
    try:
      l += len(self.temporary_buffer[tid])
    except KeyError:
      pass
    return l

  def remove(self, value):
    self._register()
    for uid_list in self.temporary_buffer.values():
      try:
        uid_list.remove(value)
      except ValueError:
        pass
    try:
      self.finished_buffer.remove(value)
    except ValueError:
      pass

  def pop(self):
    self._register()
    tid = get_ident()
    try:
      uid = self.temporary_buffer[tid].pop()
    except (KeyError, IndexError):
      uid = self.finished_buffer.pop()
    return uid

  def extend(self, iterable):
    self._register()
    tid = get_ident()
    self.temporary_buffer.setdefault(tid, []).extend(iterable)


# valid search modes for queries
FULL_TEXT_SEARCH_MODE = 'FullText'
EXACT_MATCH_SEARCH_MODE = 'ExactMatch'
KEYWORD_SEARCH_MODE = 'Keyword'


class QueryMixin:
  """
    Mixing class which implements methods which are
    common to all kinds of Queries
  """

  operator = None
  format = None
  type = None

  def getOperator(self):
    return self.operator

  def getFormat(self):
    return self.format

  def getType(self):
    return self.type

  def getLogicalOperator(self):
    return self.logical_operator

  def _quoteSQLString(self, value):
    """Return a quoted string of the value.
    """
    format = self.getFormat()
    type = self.getType()
    if format is not None and type is not None:
      if type == 'date':
        if hasattr(value, 'strftime'):
          value = value.strftime(format)
        if isinstance(value, basestring):
          value = "STR_TO_DATE('%s','%s')" % (value, format)
      if type == 'float':
        # Make sure there is no space in float values
        value = value.replace(' ','')
        value = "'%s'" % value
    else:
      if hasattr(value, 'ISO'):
        value = "'%s'" % value.ISO()
      elif hasattr(value, 'strftime'):
        value = "'%s'" % value.strftime('%Y-%m-%d %H:%M:%S')
      else:
        value = "'%s'" % sql_quote(str(value))
    return value

  def _quoteSQLKey(self, key):
    """Return a quoted string of the value.
    """
    format = self.getFormat()
    type = self.getType()
    if format is not None and type is not None:
      if type == 'date':
        key = "STR_TO_DATE(DATE_FORMAT(%s,'%s'),'%s')" % (key, format, format)
      if type == 'float':
        float_format = format.replace(' ','')
        if float_format.find('.') >= 0:
          precision = len(float_format.split('.')[1])
          key = "TRUNCATE(%s,%s)" % (key, precision)
    return key

  def asSQLExpression(self, key_alias_dict=None,
                      keyword_search_keys=None,
                      full_text_search_keys=None,
                      ignore_empty_string=1, stat__=0):
    """
      Return a dictionnary containing the keys and value types:
        'where_expression': string
        'select_expression_list': string
    """
    raise NotImplementedError

  def getSQLKeyList(self):
    """
      Return a list of keys used by this query and its subqueries.
    """
    raise NotImplementedError
  
  def getRelatedTableMapDict(self):
    """
      Return for each key used by this query (plus ones used by its
      subqueries) the table alias mapping.
    """
    raise NotImplementedError

class NegatedQuery(QueryMixin): # XXX Bad name JPS - NotQuery or NegativeQuery is better NegationQuery
  """
    Do a boolean negation of given query.
  """

  def __init__(self, query):
    self._query = query

  def asSQLExpression(self, *args, **kw):
    sql_expression_dict = self._query.asSQLExpression(*args, **kw)
    sql_expression_dict['where_expression'] = '(NOT (%s))' % \
      (sql_expression_dict['where_expression'], )
    return sql_expression_dict

  def getSQLKeyList(self, *args, **kw):
    return self._query.getSQLKeyList(*args, **kw)

  def getRelatedTableMapDict(self, *args, **kw):
    return self._query.getRelatedTableMapDict(*args, **kw)

  # asSearchTextExpression is still not implemented

allow_class(NegatedQuery)

class Query(QueryMixin):
  """
  This allow to define constraints on a sql column

  format - type date : %d/%m/%Y
           type float : 1 234.12
  """
  def __init__(self, format=None, operator=None, range=None, key=None,
                     search_mode=None, table_alias_list=None, type=None, **kw):
    self.format = format
    if operator is None:
      operator = 'OR'
    self.operator = operator
    self.range = range
    self.search_mode = search_mode
    self.table_alias_list = table_alias_list
    key_list = kw.keys()
    if len(key_list) != 1:
      raise KeyError, 'Query must have only one key'
    self.key = key_list[0]
    self.value = kw[self.key]
    self.type = type
    self.search_key = key

  def __call__(self):
    self.asSQLExpression()

  def getRange(self):
    return self.range

  def getTableAliasList(self):
    return self.table_alias_list

  def getRelatedTableMapDict(self):
    result = {}
    table_alias_list = self.getTableAliasList()
    if table_alias_list is not None:
      result[self.getKey()] = table_alias_list
    return result

  def getSearchMode(self):
    """Search mode used for Full Text search
    """
    return self.search_mode

  def asSearchTextExpression(self):
    # This will be the standard way to represent
    # complex values in listbox. Some fixed
    # point must be garanteed
    value = self.value
    if isSimpleType(value) or isinstance(value, DateTime):
      return str(value)
    elif isinstance(value, (list, tuple)):
      value = map(lambda x:str(x), value)
      return (' %s ' % self.operator).join(value)

  def asSQLExpression(self, key_alias_dict=None,
                            keyword_search_keys=None,
                            full_text_search_keys=None,
                            ignore_empty_string=1, stat__=0):
    """
    Build the sql string
    """
    sql_expression = ''
    value = self.getValue()
    key = self.getKey()
    search_key = self.search_key
    ignore_key = 0
    if key_alias_dict is not None:
      # Try to find the alias
      if key not in key_alias_dict:
        ignore_key=1
      else:
        key = key_alias_dict.get(key)
        if key is None:
          ignore_key=1
    where_expression = []
    select_expression = []
    # Default case: variable equality
    range_value = self.getRange()
    format = self.getFormat()
    if ignore_key:
      pass
    elif range_value is not None:
      if isinstance(value, (list, tuple)):
        if format is None:
          query_min = min(value)
          query_max = max(value)
        else:
          query_min = value[0]
          query_max = value[1]
      else:
        query_min=query_max=value
      query_min = self._quoteSQLString(query_min)
      query_max = self._quoteSQLString(query_max)
      if range_value == 'min' :
        where_expression.append("%s >= %s" % (key, query_min))
      elif range_value == 'max' :
        where_expression.append("%s < %s" % (key, query_max))
      elif range_value == 'minmax' :
        where_expression.append("%s >= %s and %s < %s" % (key, query_min, key, query_max))
      elif range_value == 'minngt' :
        where_expression.append("%s >= %s and %s <= %s" % (key, query_min, key, query_max))
      elif range_value == 'ngt' :
        where_expression.append("%s <= %s" % (key, query_max))
      elif range_value == 'nlt' :
        where_expression.append("%s > %s" % (key, query_max))
    elif isSimpleType(value) or isinstance(value, DateTime) \
        or (isinstance(value, (list, tuple)) and self.operator.upper() != 'IN'):
      # Convert into lists any value which contain 'OR'
      # Refer to _listGlobalActions DCWorkflow patch for example of use
      if isinstance(value, basestring) \
                and search_key != EXACT_MATCH_SEARCH_MODE:
        value = value.split(' OR ')
        value = map(lambda x:x.strip(), value)
      value_list = value
      if isSimpleType(value) or isinstance(value, DateTime):
        value_list = [value]
      # For security.
      for value in value_list:
        comparison_operator = None
        if (value != '' or not ignore_empty_string) \
                        and isinstance(value, basestring):
          if '%' in value and search_key != EXACT_MATCH_SEARCH_MODE:
            comparison_operator = 'LIKE'
          elif len(value) >= 1 and value[0:2] in ('<=','!=','>='):
            comparison_operator = value[0:2]
            value = value[2:]
          elif len(value) >= 1 and value[0] in ('=','>','<'):
            comparison_operator = value[0]
            value = value[1:]
          elif search_key == KEYWORD_SEARCH_MODE or (
                   key in keyword_search_keys and
                    search_key != EXACT_MATCH_SEARCH_MODE):
            # We must add % in the request to simulate the catalog
            comparison_operator = 'LIKE'
            value = '%%%s%%' % value
          elif search_key == FULL_TEXT_SEARCH_MODE or (
                  key in full_text_search_keys
                  and search_key != EXACT_MATCH_SEARCH_MODE):
            # We must add % in the request to simulate the catalog
            # we first check if there is a special search_mode for this key
            # incl. table name, or for all keys of that name,
            # or there is a search_mode supplied for all fulltext keys
            # or we fall back to natural mode
            search_mode=self.getSearchMode()
            if search_mode is None:
              search_mode = 'natural'
            search_mode=search_mode.lower()
            mode = full_text_search_modes.get(search_mode,'')
            where_expression.append(
                        "MATCH %s AGAINST ('%s' %s)" % (key, value, mode))
            if not stat__:
              # we return relevance as Table_Key_relevance
              select_expression.append(
                     "MATCH %s AGAINST ('%s' %s) AS %s_relevance" 
                     % (key, value, mode,key.replace('.','_')))
              # and for simplicity as Key_relevance
              if '.' in key:
                select_expression.append(
                     "MATCH %s AGAINST ('%s' %s) AS %s_relevance" % 
                     (key, value, mode,key.split('.')[1]))
          else:
            comparison_operator = '='
        elif not isinstance(value, basestring):
          comparison_operator = '='
        if comparison_operator is not None:
          key = self._quoteSQLKey(key)
          value = self._quoteSQLString(value)
          where_expression.append("%s %s %s" % 
                                  (key, comparison_operator, value))

    elif value is None:
      where_expression.append("%s is NULL" % (key))
    elif isinstance(value, (tuple, list)) and self.operator.upper() == 'IN':
      if len(value) > 1:
        escaped_value_list = [self._quoteSQLString(x) for x in value]
        escaped_value_string = ', '.join(escaped_value_list)
        where_expression.append("%s IN (%s)" % (key, escaped_value_string))
      elif len(value) == 1:
        where_expression.append("%s = %s" % (key, self._quoteSQLString(value[0])))
      else:
        where_expression.append('0') # "foo IN ()" is invalid SQL syntax, so use a "false" value.
    else:
      where_expression.append("%s = %s" % 
           (self._quoteSQLKey(key), self._quoteSQLString(value)))

    if len(where_expression)>0:
      if len(where_expression)==1:
        where_expression = where_expression[0]
      else:
        where_expression = '(%s)' % (' %s ' % self.getOperator()).join(where_expression)
    else:
      where_expression = '1' # It is better to have a valid default
    return {'where_expression':where_expression,
            'select_expression_list':select_expression}

  def getKey(self):
    return self.key

  def getValue(self):
    return self.value

  def getSQLKeyList(self):
    """
    Returns the list of keys used by this
    instance
    """
    return [self.getKey()]

allow_class(Query)

class ComplexQuery(QueryMixin):
  """
  Used in order to concatenate many queries
  """
  def __init__(self, *args, **kw):
    # XXX: python weirdness
    # >>> def foo(a='a', *args):
    # ...   pass
    # ...
    # >>> foo('something', a='test')
    # TypeError: foo() got multiple values for keyword argument 'a'
    self.query_list = args
    self.operator = kw.pop('operator', 'AND')
    # XXX: What is that used for ?! It's utterly dangerous.
    self.__dict__.update(kw)

  def __call__(self):
    self.asSQLExpression()

  def getQueryList(self):
    return self.query_list

  def getRelatedTableMapDict(self):
    result = {}
    for query in self.getQueryList():
      if not(isinstance(query, basestring)):
        result.update(query.getRelatedTableMapDict())
    return result

  def asSQLExpression(self, key_alias_dict=None,
                            ignore_empty_string=1,
                            keyword_search_keys=None,
                            full_text_search_keys=None,
                            stat__=0):
    """
    Build the sql string
    """
    sql_expression_list = []
    select_expression_list = []
    for query in self.getQueryList():
      if isinstance(query, basestring):
        sql_expression_list.append(query)
      else:
        query_result = query.asSQLExpression( key_alias_dict=key_alias_dict,
                               ignore_empty_string=ignore_empty_string,
                               keyword_search_keys=keyword_search_keys,
                               full_text_search_keys=full_text_search_keys,
                               stat__=stat__)
        sql_expression_list.append(query_result['where_expression'])
        select_expression_list.extend(query_result['select_expression_list'])
    operator = self.getOperator()
    result = {'where_expression':('(%s)' %  \
                         (' %s ' % operator).join(['(%s)' % x for x in sql_expression_list])),
              'select_expression_list':select_expression_list}
    return result

  def getSQLKeyList(self):
    """
    Returns the list of keys used by this
    instance
    """
    key_list=[]
    for query in self.getQueryList():
      if not(isinstance(query, basestring)):
        key_list.extend(query.getSQLKeyList())
    return key_list

allow_class(ComplexQuery)

class Catalog(Folder,
              Persistent,
              Acquisition.Implicit,
              ExtensionClass.Base,
              OFS.History.Historical):
  """ An Object Catalog

  An Object Catalog maintains a table of object metadata, and a
  series of manageable indexes to quickly search for objects
  (references in the metadata) that satisfy a search where_expression.

  This class is not Zope specific, and can be used in any python
  program to build catalogs of objects.  Note that it does require
  the objects to be Persistent, and thus must be used with ZODB3.

  uid -> the (local) universal ID of objects
  path -> the (local) path of objects

  If you pass it a keyword argument which is present in sql_catalog_full_text_search_keys
  (in catalog properties), it does a MySQL full-text search.
  Additionally you can pass it a search_mode argument ('natural', 'in_boolean_mode'
  or 'with_query_expansion') to use an advanced search mode ('natural'
  is the default).
  search_mode arg can be given for all full_text keys, or for a specific key by naming
  the argument search_mode_KeyName, or even more specifically, search_mode_Table.Key
  or search_mode_Table_Key


  brain defined in methods...

  TODO:

    - optmization: indexing objects should be deferred
      until timeout value or end of transaction
  """
  meta_type = "SQLCatalog"
  icon = 'misc_/ZCatalog/ZCatalog.gif' # FIXME: use a different icon
  security = ClassSecurityInfo()

  manage_options = (
    {'label': 'Contents',       # TAB: Contents
     'action': 'manage_main',
     'help': ('OFSP','ObjectManager_Contents.stx')},
    {'label': 'Catalog',      # TAB: Catalogged Objects
     'action': 'manage_catalogView',
     'help':('ZCatalog','ZCatalog_Cataloged-Objects.stx')},
    {'label': 'Properties',     # TAB: Properties
     'action': 'manage_propertiesForm',
     'help': ('OFSP','Properties.stx')},
    {'label': 'Filter',     # TAB: Filter
     'action': 'manage_catalogFilter',},
    {'label': 'Find Objects',     # TAB: Find Objects
     'action': 'manage_catalogFind',
     'help':('ZCatalog','ZCatalog_Find-Items-to-ZCatalog.stx')},
    {'label': 'Advanced',       # TAB: Advanced
     'action': 'manage_catalogAdvanced',
     'help':('ZCatalog','ZCatalog_Advanced.stx')},
    {'label': 'Undo',         # TAB: Undo
     'action': 'manage_UndoForm',
     'help': ('OFSP','Undo.stx')},
    {'label': 'Security',       # TAB: Security
     'action': 'manage_access',
     'help': ('OFSP','Security.stx')},
    {'label': 'Ownership',      # TAB: Ownership
     'action': 'manage_owner',
     'help': ('OFSP','Ownership.stx'),}
    ) + OFS.History.Historical.manage_options

  __ac_permissions__= (

    ('Manage ZCatalog Entries',
     ['manage_catalogObject', 'manage_uncatalogObject',

      'manage_catalogView', 'manage_catalogFind',
      'manage_catalogFilter',
      'manage_catalogAdvanced',

      'manage_catalogReindex', 'manage_catalogFoundItems',
      'manage_catalogClear',
      'manage_main',
      'manage_editFilter',
      ],
     ['Manager']),

    ('Search ZCatalog',
     ['searchResults', '__call__', 'uniqueValuesFor',
      'all_meta_types', 'valid_roles',
      'getCatalogSearchTableIds',
      'getFilterableMethodList',],
     ['Anonymous', 'Manager']),

    ('Import/Export objects',
     ['manage_exportProperties', 'manage_importProperties', ],
     ['Manager']),

    )

  _properties = (
    { 'id'      : 'title',
      'description' : 'The title of this catalog',
      'type'    : 'string',
      'mode'    : 'w' },

    # Z SQL Methods
    { 'id'      : 'sql_catalog_produce_reserved',
      'description' : 'A method to produce new uid values in advance',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_clear_reserved',
      'description' : 'A method to clear reserved uid values',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_reserve_uid',
      'description' : 'A method to reserve a uid value',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_delete_uid',
      'description' : 'A method to delete a uid value',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_object_list',
      'description' : 'Methods to be called to catalog the list of objects',
      'type'    : 'multiple selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_uncatalog_object',
      'description' : 'Methods to be called to uncatalog an object',
      'type'    : 'multiple selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_translation_list',
      'description' : 'Methods to be called to catalog the list of translation objects',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_delete_translation_list',
      'description' : 'Methods to be called to delete translations',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_clear_catalog',
      'description' : 'The methods which should be called to clear the catalog',
      'type'    : 'multiple selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_record_object_list',
      'description' : 'Method to record catalog information',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_read_recorded_object_list',
      'description' : 'Method to get recorded information',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_delete_recorded_object_list',
      'description' : 'Method to delete recorded information',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_search_results',
      'description' : 'Main method to search the catalog',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_search_security',
      'description' : 'Main method to search security',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_search_tables',
      'description' : 'Tables to join in the result',
      'type'    : 'multiple selection',
      'select_variable' : 'getTableIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_search_result_keys',
      'description' : 'Keys to display in the result',
      'type'    : 'multiple selection',
      'select_variable' : 'getResultColumnIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_count_results',
      'description' : 'Main method to search the catalog',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_getitem_by_path',
      'description' : 'Get a catalog brain by path',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_getitem_by_uid',
      'description' : 'Get a catalog brain by uid',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_tables',
      'description' : 'Method to get the main catalog tables',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_schema',
      'description' : 'Method to get the main catalog schema',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_index',
      'description' : 'Method to get the main catalog index',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_unique_values',
      'description' : 'Find unique disctinct values in a column',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_paths',
      'description' : 'List all object paths in catalog',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_keyword_search_keys',
      'description' : 'Columns which should be considered as full text search',
      'type'    : 'multiple selection',
      'select_variable' : 'getColumnIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_full_text_search_keys',
      'description' : 'Columns which should be considered as full text search',
      'type'    : 'multiple selection',
      'select_variable' : 'getColumnIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_request_keys',
      'description' : 'Columns which should be ignore in the REQUEST in order to accelerate caching',
      'type'    : 'multiple selection',
      'select_variable' : 'getColumnIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_multivalue_keys',
      'description' : 'Keys which hold multiple values',
      'type'    : 'multiple selection',
      'select_variable' : 'getColumnIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_index_on_order_keys',
      'description' : 'Columns which should be used by specifying an index when sorting on them',
      'type'    : 'multiple selection',
      'select_variable' : 'getSortColumnIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_topic_search_keys',
      'description' : 'Columns which should be considered as topic index',
      'type'    : 'lines',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_related_keys',
      'title'   : 'Related keys',
      'description' : 'Additional columns obtained through joins',
      'type'    : 'lines',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_scriptable_keys',
      'title'   : 'Related keys',
      'description' : 'Virtual columns to generate scriptable scriptable queries',
      'type'    : 'lines',
      'mode'    : 'w' },
  )

  sql_catalog_produce_reserved = ''
  sql_catalog_delete_uid = ''
  sql_catalog_clear_reserved = ''
  sql_catalog_reserve_uid = ''
  sql_catalog_object_list = ()
  sql_uncatalog_object = ()
  sql_clear_catalog = ()
  sql_catalog_translation_list = ''
  sql_delete_translation_list = ''
  sql_record_object_list = ''
  sql_read_recorded_object_list = ''
  sql_delete_recorded_object_list = ''
  sql_search_results = ''
  sql_search_security = ''
  sql_count_results = ''
  sql_getitem_by_path = ''
  sql_getitem_by_uid = ''
  sql_catalog_tables = ''
  sql_search_tables = ()
  sql_catalog_schema = ''
  sql_catalog_index = ''
  sql_unique_values = ''
  sql_catalog_paths = ''
  sql_catalog_keyword_search_keys =  ()
  sql_catalog_full_text_search_keys = ()
  sql_catalog_request_keys = ()
  sql_search_result_keys = ()
  sql_catalog_topic_search_keys = ()
  sql_catalog_multivalue_keys = ()
  sql_catalog_index_on_order_keys = ()
  sql_catalog_related_keys = ()
  sql_catalog_scriptable_keys = ()

  # These are ZODB variables, so shared by multiple Zope instances.
  # This is set to the last logical time when clearReserved is called.
  _last_clear_reserved_time = 0
  # This is to record the maximum value of uids. Because this uses the class Length
  # in BTrees.Length, this does not generate conflict errors.
  _max_uid = None

  # These are class variable on memory, so shared only by threads in the same Zope instance.
  # This is set to the time when reserved uids are cleared in this Zope instance.
  _local_clear_reserved_time = None
  # This is used for exclusive access to the list of reserved uids.
  _reserved_uid_lock = allocate_lock()
  # This is an instance id which specifies who owns which reserved uids.
  _instance_id = getattr(getConfiguration(), 'instance_id', None)

  manage_catalogView = DTMLFile('dtml/catalogView',globals())
  manage_catalogFilter = DTMLFile('dtml/catalogFilter',globals())
  manage_catalogFind = DTMLFile('dtml/catalogFind',globals())
  manage_catalogAdvanced = DTMLFile('dtml/catalogAdvanced', globals())

  def __init__(self, id, title='', container=None):
    if container is not None:
      self=self.__of__(container)
    self.id=id
    self.title=title
    self.schema = {}  # mapping from attribute name to column
    self.names = {}   # mapping from column to attribute name
    self.indexes = {}   # empty mapping
    self.filter_dict = PersistentMapping()

  def manage_exportProperties(self, REQUEST=None, RESPONSE=None):
    """
      Export properties to an XML file.
    """
    f = StringIO()
    f.write('<?xml version="1.0"?>\n<SQLCatalogData>\n')
    property_id_list = self.propertyIds()
    # Get properties and values
    property_list = []
    for property_id in property_id_list:
      value = self.getProperty(property_id)
      if value is not None:
        property_list.append((property_id, value))
    # Sort for easy diff
    property_list.sort(lambda x, y: cmp(x[0], y[0]))
    for property in property_list:
      property_id = property[0]
      value       = property[1]
      if isinstance(value, basestring):
        f.write('  <property id=%s type="str">%s</property>\n' % (quoteattr(property_id), escape(value)))
      elif isinstance(value, (tuple, list)):
        f.write('  <property id=%s type="tuple">\n' % quoteattr(property_id))
        # Sort for easy diff
        item_list = []
        for item in value:
          if isinstance(item, basestring):
            item_list.append(item)
        item_list.sort()
        for item in item_list:
          f.write('    <item type="str">%s</item>\n' % escape(str(item)))
        f.write('  </property>\n')
    # XXX Although filters are not properties, output filters here.
    # XXX Ideally, filters should be properties in Z SQL Methods, shouldn't they?
    if hasattr(self, 'filter_dict'):
      filter_list = []
      for filter_id in self.filter_dict.keys():
        filter_definition = self.filter_dict[filter_id]
        filter_list.append((filter_id, filter_definition))
      # Sort for easy diff
      filter_list.sort(lambda x, y: cmp(x[0], y[0]))
      for filter_item in filter_list:
        filter_id  = filter_item[0]
        filter_def = filter_item[1]
        if not filter_def['filtered']:
          # If a filter is not activated, no need to output it.
          continue
        if not filter_def['expression']:
          # If the expression is not specified, meaningless to specify it.
          continue
        f.write('  <filter id=%s expression=%s />\n' % (quoteattr(filter_id), quoteattr(filter_def['expression'])))
        # For now, portal types are not exported, because portal types are too specific to each site.
    f.write('</SQLCatalogData>\n')

    if RESPONSE is not None:
      RESPONSE.setHeader('Content-type','application/data')
      RESPONSE.setHeader('Content-Disposition',
                          'inline;filename=properties.xml')
    return f.getvalue()

  def manage_importProperties(self, file):
    """
      Import properties from an XML file.
    """
    f = open(file)
    try:
      doc = parse(f)
      root = doc.documentElement
      try:
        for prop in root.getElementsByTagName("property"):
          id = prop.getAttribute("id")
          type = prop.getAttribute("type")
          if not id or not hasattr(self, id):
            raise CatalogError, 'unknown property id %r' % (id,)
          if type not in ('str', 'tuple'):
            raise CatalogError, 'unknown property type %r' % (type,)
          if type == 'str':
            value = ''
            for text in prop.childNodes:
              if text.nodeType == text.TEXT_NODE:
                value = str(text.data)
                break
          else:
            value = []
            for item in prop.getElementsByTagName("item"):
              item_type = item.getAttribute("type")
              if item_type != 'str':
                raise CatalogError, 'unknown item type %r' % (item_type,)
              for text in item.childNodes:
                if text.nodeType == text.TEXT_NODE:
                  value.append(str(text.data))
                  break
            value = tuple(value)

          setattr(self, id, value)

        if not hasattr(self, 'filter_dict'):
          self.filter_dict = PersistentMapping()
        for filt in root.getElementsByTagName("filter"):
          id = str(filt.getAttribute("id"))
          expression = filt.getAttribute("expression")
          if not self.filter_dict.has_key(id):
            self.filter_dict[id] = PersistentMapping()
          self.filter_dict[id]['filtered'] = 1
          self.filter_dict[id]['type'] = []
          if expression:
            expr_instance = Expression(expression)
            self.filter_dict[id]['expression'] = expression
            self.filter_dict[id]['expression_instance'] = expr_instance
          else:
            self.filter_dict[id]['expression'] = ""
            self.filter_dict[id]['expression_instance'] = None
      finally:
        doc.unlink()
    finally:
      f.close()

  def manage_historyCompare(self, rev1, rev2, REQUEST,
                            historyComparisonResults=''):
    return Catalog.inheritedAttribute('manage_historyCompare')(
          self, rev1, rev2, REQUEST,
          historyComparisonResults=OFS.History.html_diff(
              pprint.pformat(rev1.__dict__),
              pprint.pformat(rev2.__dict__)))

  def _clearSecurityCache(self):
    self.security_uid_dict = OIBTree()
    self.security_uid_index = None

  security.declarePrivate('getSecurityUid')
  def getSecurityUid(self, wrapped_object):
    """
      Cache a uid for each security permission

      We try to create a unique security (to reduce number of lines)
      and to assign security only to root document
    """
    # Get security information
    allowed_roles_and_users = wrapped_object.allowedRolesAndUsers()
    # Sort it
    allowed_roles_and_users = list(allowed_roles_and_users)
    allowed_roles_and_users.sort()
    allowed_roles_and_users = tuple(allowed_roles_and_users)
    # Make sure no duplicates
    if getattr(aq_base(self), 'security_uid_dict', None) is None:
      self._clearSecurityCache()
    if self.security_uid_dict.has_key(allowed_roles_and_users):
      return (self.security_uid_dict[allowed_roles_and_users], None)
    # If the id_tool is there, it is better to use it, it allows
    # to create many new security uids by the same time
    # because with this tool we are sure that we will have 2 different
    # uids if two instances are doing this code in the same time
    id_tool = getattr(self.getPortalObject(), 'portal_ids', None)
    if id_tool is not None:
      default = 1
      # We must keep compatibility with existing sites
      previous_security_uid = getattr(self, 'security_uid_index', None)
      if previous_security_uid is not None:
        # At some point, it was a Length
        if isinstance(previous_security_uid, Length):
          default = previous_security_uid() + 1
        else:
          default = previous_security_uid
      security_uid = id_tool.generateNewLengthId(id_group='security_uid_index',
                                        default=default)
    else:
      previous_security_uid = getattr(self, 'security_uid_index', None)
      if previous_security_uid is None:
        previous_security_uid = 0
      # At some point, it was a Length
      if isinstance(previous_security_uid, Length):
        previous_security_uid = previous_security_uid()
      security_uid = previous_security_uid + 1
      self.security_uid_index = security_uid
    self.security_uid_dict[allowed_roles_and_users] = security_uid
    return (security_uid, allowed_roles_and_users)

  def clear(self):
    """
    Clears the catalog by calling a list of methods
    """
    methods = self.sql_clear_catalog
    for method_name in methods:
      method = getattr(self, method_name)
      try:
        method()
      except ConflictError:
        raise
      except:
        LOG('SQLCatalog', WARNING,
            'could not clear catalog with %s' % method_name, error=sys.exc_info())

    # Reserved uids have been removed.
    self.clearReserved()

    # Add a dummy item so that SQLCatalog will not use existing uids again.
    self.insertMaxUid()

    # Remove the cache of catalog schema.
    if hasattr(self, '_v_catalog_schema_dict') :
      del self._v_catalog_schema_dict

    self._clearSecurityCache()

  def insertMaxUid(self):
    """
      Add a dummy item so that SQLCatalog will not use existing uids again.
    """
    if self._max_uid is not None and self._max_uid() != 0:
      method_id = self.sql_catalog_reserve_uid
      method = getattr(self, method_id)
      self._max_uid.change(1)
      method(uid = [self._max_uid()])

  def clearReserved(self):
    """
    Clears reserved uids
    """
    method_id = self.sql_catalog_clear_reserved
    method = getattr(self, method_id)
    try:
      method()
    except ConflictError:
      raise
    except:
      LOG('SQLCatalog', WARNING,
          'could not clear reserved catalog with %s' % \
              method_id, error=sys.exc_info())
      raise
    self._last_clear_reserved_time += 1

  def __getitem__(self, uid):
    """
    Get an object by UID
    Note: brain is defined in Z SQL Method object
    """
    method = getattr(self,  self.sql_getitem_by_uid)
    search_result = method(uid = uid)
    if len(search_result) > 0:
      return search_result[0]
    raise KeyError, uid

  def editSchema(self, names_list):
    """
    Builds a schema from a list of strings
    Splits each string to build a list of attribute names
    Columns on the database should not change during this operations
    """
    i = 0
    schema = {}
    names = {}
    for cid in self.getColumnIds():
      name_list = []
      for name in names_list[i].split():
        schema[name] = cid
        name_list += [name,]
      names[cid] = tuple(name_list)
      i += 1
    self.schema = schema
    self.names = names

  def getCatalogSearchTableIds(self):
    """Return selected tables of catalog which are used in JOIN.
       catalaog is always first
    """
    search_tables = self.sql_search_tables
    if len(search_tables) > 0:
      if search_tables[0] != 'catalog':
        result = ['catalog']
        for t in search_tables:
          if t != 'catalog':
            result.append(t)
        self.sql_search_tables = result
    else:
      self.sql_search_tables = ['catalog']

    return self.sql_search_tables

  security.declarePublic('getCatalogSearchResultKeys')
  def getCatalogSearchResultKeys(self):
    """Return search result keys.
    """
    return self.sql_search_result_keys

  def _getCatalogSchema(self, table=None):
    # XXX: Using a volatile as a cache makes it impossible to flush
    # consistently on all connections containing the volatile. Another
    # caching scheme must be used here.
    catalog_schema_dict = getattr(aq_base(self), '_v_catalog_schema_dict', {})

    if table not in catalog_schema_dict:
      result_list = []
      try:
        method_name = self.sql_catalog_schema
        method = getattr(self, method_name)
        #LOG('_getCatalogSchema', 0, 'method_name = %r, method = %r, table = %r' % (method_name, method, table))
        search_result = method(table=table)
        for c in search_result:
          result_list.append(c.Field)
      except ConflictError:
        raise
      except:
        LOG('SQLCatalog', WARNING, '_getCatalogSchema failed with the method %s' % method_name, error=sys.exc_info())
        pass
      catalog_schema_dict[table] = tuple(result_list)
      self._v_catalog_schema_dict= catalog_schema_dict

    return catalog_schema_dict[table]

  def getColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids
    """
    def _getColumnIds():
      keys = {}
      for table in self.getCatalogSearchTableIds():
        field_list = self._getCatalogSchema(table=table)
        for field in field_list:
          keys[field] = 1
          keys['%s.%s' % (table, field)] = 1  # Is this inconsistent ?
      for related in self.getSQLCatalogRelatedKeyList():
        related_tuple = related.split('|')
        related_key = related_tuple[0].strip()
        keys[related_key] = 1
      for scriptable in self.getSQLCatalogScriptableKeyList():
        scriptable_tuple = scriptable.split('|')
        scriptable = scriptable_tuple[0].strip()
        keys[scriptable] = 1
      keys = keys.keys()
      keys.sort()
      return keys
    return CachingMethod(_getColumnIds, id='SQLCatalog.getColumnIds', cache_factory='erp5_content_long')()

  def getColumnMap(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids
    """
    def _getColumnMap():
      keys = {}
      for table in self.getCatalogSearchTableIds():
        field_list = self._getCatalogSchema(table=table)
        for field in field_list:
          key = field
          if not keys.has_key(key): keys[key] = []
          keys[key].append(table)
          key = '%s.%s' % (table, key)
          if not keys.has_key(key): keys[key] = []
          keys[key].append(table) # Is this inconsistent ?
      return keys
    return CachingMethod(_getColumnMap, id='SQLCatalog.getColumnMap', cache_factory='erp5_content_long')()

  def getResultColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids
    """
    keys = {}
    for table in self.getCatalogSearchTableIds():
      field_list = self._getCatalogSchema(table=table)
      for field in field_list:
        keys['%s.%s' % (table, field)] = 1
    keys = keys.keys()
    keys.sort()
    return keys

  def getSortColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids that can be used for a sort
    """
    keys = {}
    for table in self.getTableIds():
      field_list = self._getCatalogSchema(table=table)
      for field in field_list:
        keys['%s.%s' % (table, field)] = 1
    keys = keys.keys()
    keys.sort()
    return keys

  def getTableIds(self):
    """
    Calls the show table method and returns dictionnary of
    Field Ids
    """
    keys = []
    method_name = self.sql_catalog_tables
    try:
      method = getattr(self,  method_name)
      search_result = method()
      for c in search_result:
        keys.append(c[0])
    except ConflictError:
      raise
    except:
      pass
    return keys

  def getUIDBuffer(self, force_new_buffer=False):
    global global_uid_buffer_dict
    klass = self.__class__
    assert klass._reserved_uid_lock.locked()
    assert getattr(self, 'aq_base', None) is not None
    instance_key = self.getPhysicalPath()
    if instance_key not in global_uid_buffer_dict:
      global_uid_buffer_dict[instance_key] = {}
    uid_buffer_dict = global_uid_buffer_dict[instance_key]
    thread_key = get_ident()
    if force_new_buffer or thread_key not in uid_buffer_dict:
      uid_buffer_dict[thread_key] = UidBuffer()
    return uid_buffer_dict[thread_key]
  
  # the cataloging API
  def produceUid(self):
    """
      Produces reserved uids in advance
    """
    klass = self.__class__
    assert klass._reserved_uid_lock.locked()
    # This checks if the list of local reserved uids was cleared after clearReserved
    # had been called.
    force_new_buffer = (klass._local_clear_reserved_time != self._last_clear_reserved_time)
    uid_buffer = self.getUIDBuffer(force_new_buffer=force_new_buffer)
    klass._local_clear_reserved_time = self._last_clear_reserved_time
    if len(uid_buffer) == 0:
      id_tool = getattr(self.getPortalObject(), 'portal_ids', None)
      if id_tool is not None:
        if self._max_uid is None:
          self._max_uid = Length()
        uid_list = id_tool.generateNewLengthIdList(id_group='catalog_uid',
                     id_count=UID_BUFFER_SIZE, default=self._max_uid())
        # TODO: if this method is kept and former uid allocation code is
        # discarded, self._max_uid duplicates work done by portal_ids: it
        # already keeps track of the highest allocated number for all id
        # generator groups.
      else:
        method_id = self.sql_catalog_produce_reserved
        method = getattr(self, method_id)
        # Generate an instance id randomly. Note that there is a small possibility that this
        # would conflict with others.
        random_factor_list = [time.time(), os.getpid(), os.times()]
        try:
          random_factor_list.append(os.getloadavg())
        except (OSError, AttributeError): # AttributeError is required under cygwin
          pass
        instance_id = md5.new(str(random_factor_list)).hexdigest()
        uid_list = [x.uid for x in method(count = UID_BUFFER_SIZE, instance_id = instance_id) if x.uid != 0]
      uid_buffer.extend(uid_list)

  def isIndexable(self):
    """
    This is required to check in many methods that
    the site root and zope root are indexable
    """
    zope_root = self.getZopeRoot()
    site_root = self.getSiteRoot() # XXX-JPS - Why don't we use getPortalObject here ?

    root_indexable = int(getattr(zope_root, 'isIndexable', 1))
    site_indexable = int(getattr(site_root, 'isIndexable', 1))
    if not (root_indexable and site_indexable):
      return False
    return True

  def getSiteRoot(self):
    """
    Returns the root of the site
    """
    if withCMF:
      site_root = getToolByName(self, 'portal_url').getPortalObject()
    else:
      site_root = self.aq_parent
    return site_root

  def getZopeRoot(self):
    """
    Returns the root of the zope
    """
    if withCMF:
      zope_root = getToolByName(self, 'portal_url').getPortalObject().aq_parent
    else:
      zope_root = self.getPhysicalRoot()
    return zope_root

  def newUid(self):
    """
      This is where uid generation takes place. We should consider a multi-threaded environment
      with multiple ZEO clients on a single ZEO server.

      The main risk is the following:

      - objects a/b/c/d/e/f are created (a is parent of b which is parent of ... of f)

      - one reindexing node N1 starts reindexing f

      - another reindexing node N2 starts reindexing e

      - there is a strong risk that N1 and N2 start reindexing at the same time
        and provide different uid values for a/b/c/d/e

      Similar problems may happen with relations and acquisition of uid values (ex. order_uid)
      with the risk of graph loops
    """
    if not self.isIndexable():
      return None

    klass = self.__class__
    try:
      klass._reserved_uid_lock.acquire()
      self.produceUid()
      uid_buffer = self.getUIDBuffer()
      if len(uid_buffer) > 0:
        uid = uid_buffer.pop()
        # Vincent added this 2006/01/25
        #if uid > 4294967296: # 2**32
        #if uid > 10000000: # arbitrary level : below it's normal, above it's suspicious
        #   LOG('SQLCatalog', WARNING, 'Newly generated UID (%s) seems too big ! - vincent' % (uid,))
        #   raise RuntimeError, 'Newly generated UID (%s) seems too big ! - vincent' % (uid,)
        # end
        if self._max_uid is None:
          self._max_uid = Length()
        if uid > self._max_uid():
          self._max_uid.set(uid)
        return long(uid)
      else:
        raise CatalogError("Could not retrieve new uid")
    finally:
      klass._reserved_uid_lock.release()

  def manage_catalogObject(self, REQUEST, RESPONSE, URL1, urls=None):
    """ index Zope object(s) that 'urls' point to """
    if urls:
      if isinstance(urls, str):
        urls=(urls,)

      for url in urls:
        obj = self.resolve_path(url)
        if not obj:
          obj = self.resolve_url(url, REQUEST)
        if obj is not None:
          self.aq_parent.catalog_object(obj, url, sql_catalog_id=self.id)

    RESPONSE.redirect(URL1 + '/manage_catalogView?manage_tabs_message=Object%20Cataloged')

  def manage_uncatalogObject(self, REQUEST, RESPONSE, URL1, urls=None):
    """ removes Zope object(s) 'urls' from catalog """

    if urls:
      if isinstance(urls, str):
        urls=(urls,)

      for url in urls:
        self.aq_parent.uncatalog_object(url, sql_catalog_id=self.id)

    RESPONSE.redirect(URL1 + '/manage_catalogView?manage_tabs_message=Object%20Uncataloged')

  def manage_catalogReindex(self, REQUEST, RESPONSE, URL1):
    """ clear the catalog, then re-index everything """
    elapse = time.time()
    c_elapse = time.clock()

    self.aq_parent.refreshCatalog(clear=1, sql_catalog_id=self.id)

    elapse = time.time() - elapse
    c_elapse = time.clock() - c_elapse

    RESPONSE.redirect(URL1 +
              '/manage_catalogAdvanced?manage_tabs_message=' +
              urllib.quote('Catalog Updated<br>'
                     'Total time: %s<br>'
                     'Total CPU time: %s' % (`elapse`, `c_elapse`)))

  def manage_catalogClear(self, REQUEST=None, RESPONSE=None,
                          URL1=None, sql_catalog_id=None):
    """ clears the whole enchilada """
    self.beforeCatalogClear()

    self.clear()

    if RESPONSE and URL1:
      RESPONSE.redirect('%s/manage_catalogAdvanced?' \
                        'manage_tabs_message=Catalog%%20Cleared' % URL1)

  def manage_catalogClearReserved(self, REQUEST=None, RESPONSE=None, URL1=None):
    """ clears reserved uids """
    self.clearReserved()

    if RESPONSE and URL1:
      RESPONSE.redirect('%s/manage_catalogAdvanced?' \
                        'manage_tabs_message=Catalog%%20Cleared' % URL1)

  def manage_catalogFoundItems(self, REQUEST, RESPONSE, URL2, URL1,
                 obj_metatypes=None,
                 obj_ids=None, obj_searchterm=None,
                 obj_expr=None, obj_mtime=None,
                 obj_mspec=None, obj_roles=None,
                 obj_permission=None):
    """ Find object according to search criteria and Catalog them
    """
    elapse = time.time()
    c_elapse = time.clock()

    words = 0
    obj = REQUEST.PARENTS[1]
    path = string.join(obj.getPhysicalPath(), '/')

    results = self.aq_parent.ZopeFindAndApply(obj,
                    obj_metatypes=obj_metatypes,
                    obj_ids=obj_ids,
                    obj_searchterm=obj_searchterm,
                    obj_expr=obj_expr,
                    obj_mtime=obj_mtime,
                    obj_mspec=obj_mspec,
                    obj_permission=obj_permission,
                    obj_roles=obj_roles,
                    search_sub=1,
                    REQUEST=REQUEST,
                    apply_func=self.aq_parent.catalog_object,
                    apply_path=path,
                    sql_catalog_id=self.id)

    elapse = time.time() - elapse
    c_elapse = time.clock() - c_elapse

    RESPONSE.redirect(URL1 + '/manage_catalogView?manage_tabs_message=' +
              urllib.quote('Catalog Updated<br>Total time: %s<br>Total CPU time: %s' % (`elapse`, `c_elapse`)))

  def catalogObject(self, object, path, is_object_moved=0):
    """Add an object to the Catalog by calling all SQL methods and
    providing needed arguments.

    'object' is the object to be catalogged."""
    self._catalogObjectList([object])

  def catalogObjectList(self, object_list, method_id_list=None, 
                        disable_cache=0, check_uid=1, idxs=None):
    """Add objects to the Catalog by calling all SQL methods and
    providing needed arguments.

      method_id_list : specify which methods should be used. If not
                       set, it will take the default value of portal_catalog.

      disable_cache : do not use cache, so values will be computed each time,
                      only useful in some particular cases, most of the time
                      you don't need to use it.

    Each element of 'object_list' is an object to be catalogged.

    'uid' is the unique Catalog identifier for this object.
    
    Note that this method calls _catalogObjectList with fragments of
    the object list, because calling _catalogObjectList with too many
    objects at a time bloats the process's memory consumption, due to
    caching."""
    # XXX 300 is arbitrary.
    for i in xrange(0, len(object_list), OBJECT_LIST_SIZE):
      self._catalogObjectList(object_list[i:i + OBJECT_LIST_SIZE],
                              method_id_list=method_id_list,
                              disable_cache=disable_cache,
                              check_uid=check_uid,
                              idxs=idxs)
    
  def _catalogObjectList(self, object_list, method_id_list=None, 
                         disable_cache=0, check_uid=1, idxs=None):
    """This is the real method to catalog objects.

    XXX: For now newUid is used to allocated UIDs. Is this good?
    Is it better to INSERT then SELECT?"""
    LOG('SQLCatalog', TRACE, 'catalogging %d objects' % len(object_list))
    #LOG('catalogObjectList', 0, 'called with %r' % (object_list,))

    if idxs not in (None, []):
      LOG('ZSLQCatalog.SQLCatalog:catalogObjectList', WARNING, 
          'idxs is ignored in this function and is only provided to be compatible with CMFCatalogAware.reindexObject.')

    if not self.isIndexable():
      return None

    portal_catalog = self.getSiteRoot().portal_catalog # XXX-JPS - This is a hardcoded name. Weird
                                                       # Isn't self == self.getSiteRoot().portal_catalog
                                                       # in this case ?

    # Reminder about optimization: It might be possible to issue just one
    # query to get enought results to check uid & path consistency.
    path_uid_dict = {}
    uid_path_dict = {}

    if check_uid:
      path_list = []
      path_list_append = path_list.append
      uid_list = []
      uid_list_append = uid_list.append
      for object in object_list:
        path = object.getPath()
        if path is not None:
          path_list_append(path)
        uid = object.uid
        if uid is not None:
          uid_list_append(uid)
      path_uid_dict = self.getUidDictForPathList(path_list=path_list)
      uid_path_dict = self.getPathDictForUidList(uid_list=uid_list)

    for object in object_list:
      if not getattr(aq_base(object), 'uid', None):
        try:
          object.uid = self.newUid()
        except ConflictError:
          raise
        except:
          raise RuntimeError, 'could not set missing uid for %r' % (object,)
      elif check_uid:
        uid = object.uid
        path = object.getPath()
        index = path_uid_dict.get(path, None)
        try:
          index = long(index)
        except TypeError:
          index = None
        if index is not None and index < 0:
          raise CatalogError, 'A negative uid %d is used for %s. Your catalog is broken. Recreate your catalog.' % (index, path)
        if index:
          if uid != index or isinstance(uid, int):
            # We want to make sure that uid becomes long if it is an int
            LOG('SQLCatalog', WARNING, 'uid of %r changed from %r (property) to %r (catalog, by path) !!! This can be fatal. You should reindex the whole site immediately.' % (object, uid, index))
            uid = index
            object.uid = uid
        else:
          # Make sure no duplicates - ie. if an object with different path has same uid, we need a new uid
          # This can be very dangerous with relations stored in a category table (CMFCategory)
          # This is why we recommend completely reindexing subobjects after any change of id
          if uid in uid_path_dict:
            catalog_path = uid_path_dict.get(uid)
          else:
            catalog_path = self.getPathForUid(uid)
          #LOG('catalogObject', 0, 'uid = %r, catalog_path = %r' % (uid, catalog_path))
          if catalog_path == "reserved":
            # Reserved line in catalog table
            klass = self.__class__
            try:
              klass._reserved_uid_lock.acquire()
              uid_buffer = self.getUIDBuffer()
              if uid_buffer is not None:
                # This is the case where:
                #   1. The object got an uid.
                #   2. The catalog was cleared.
                #   3. The catalog produced the same reserved uid.
                #   4. The object was reindexed.
                # In this case, the uid is not reserved any longer, but
                # SQLCatalog believes that it is still reserved. So it is
                # necessary to remove the uid from the list explicitly.
                try:
                  uid_buffer.remove(uid)
                except ValueError:
                  pass
            finally:
              klass._reserved_uid_lock.release()
          elif catalog_path is not None:
            # An uid conflict happened... Why?
            # can be due to path length
            if len(path) > MAX_PATH_LEN:
              LOG('SQLCatalog', WARNING, 'path of object %r is too long for catalog. You should use a shorter path.' %(object,))

            object.uid = self.newUid()
            LOG('SQLCatalog', WARNING,
                'uid of %r changed from %r to %r as old one is assigned to %s in catalog !!! This can be fatal. You should reindex the whole site immediately.' % (object, uid, object.uid, catalog_path))

    if method_id_list is None:
      method_id_list = self.sql_catalog_object_list
    econtext_cache = {}
    expression_result_cache = {}
    argument_cache = {}

    try:
      if not disable_cache:
        enableReadOnlyTransactionCache(self)

      method_kw_dict = {}
      for method_name in method_id_list:
        kw = {}
        if self.isMethodFiltered(method_name):
          catalogged_object_list = []
          type_list = self.filter_dict[method_name]['type']
          type_dict = dict(zip(type_list, type_list)) or None
          expression = self.filter_dict[method_name]['expression_instance']
          expression_cache_key_list = self.filter_dict[method_name].get('expression_cache_key', '').split()
          for object in object_list:
            # We will check if there is an filter on this
            # method, if so we may not call this zsqlMethod
            # for this object
            if type_dict is not None and object.getPortalType() not in type_dict:
              continue
            elif expression is not None:
              if expression_cache_key_list:
                # We try to save results of expressions by portal_type
                # or by anyother key which can prevent us from evaluating
                # expressions. This cache is built each time we reindex
                # objects but we could also use over multiple transactions
                # if this can improve performance significantly
                try:
                  cache_key = map(lambda key: object.getProperty(key, None), expression_cache_key_list)
                    # ZZZ - we could find a way to compute this once only
                  cache_key = (method_name, tuple(cache_key))
                  result = expression_result_cache[cache_key]
                  compute_result = 0
                except KeyError:
                  cache_result = 1
                  compute_result = 1
              else:
                cache_result = 0
                compute_result = 1
              if compute_result:
                try:
                  econtext = econtext_cache[object.uid]
                except KeyError:
                  econtext = self.getExpressionContext(object)
                  econtext_cache[object.uid] = econtext
                result = expression(econtext)
              if cache_result:
                expression_result_cache[cache_key] = result
              if not result:
                continue
            catalogged_object_list.append(object)
        else:
          catalogged_object_list = object_list

        if len(catalogged_object_list) == 0:
          continue

        method_kw_dict[method_name] = kw

        #LOG('catalogObjectList', 0, 'method_name = %s' % (method_name,))
        method = getattr(self, method_name)
        if method.meta_type in ("Z SQL Method", "LDIF Method"):
          # Build the dictionnary of values
          arguments = split(method.arguments_src)
        elif method.meta_type == "Script (Python)":
          arguments = \
            method.func_code.co_varnames[:method.func_code.co_argcount]
        else:
          arguments = []
        for arg in arguments:
          value_list = []
          append = value_list.append
          for object in catalogged_object_list:
            try:
              value = argument_cache[(object.uid, arg)]
            except KeyError:
              try:
                value = getattr(object, arg, None)
                if callable(value):
                  value = value()
              except ConflictError:
                raise
              except:
                value = None
              if not disable_cache:
                argument_cache[(object.uid, arg)] = value
            append(value)
          kw[arg] = value_list

      for method_name in method_kw_dict.keys():
        kw = method_kw_dict[method_name]
        method = getattr(self, method_name)
        method = aq_base(method).__of__(portal_catalog) # Use method in
                # the context of portal_catalog
        # Alter/Create row
        try:
          #start_time = DateTime()
          #LOG('catalogObjectList', DEBUG, 'kw = %r, method_name = %r' % (kw, method_name))
          method(**kw)
          #end_time = DateTime()
          #if method_name not in profile_dict:
          #  profile_dict[method_name] = end_time.timeTime() - start_time.timeTime()
          #else:
          #  profile_dict[method_name] += end_time.timeTime() - start_time.timeTime()
          #LOG('catalogObjectList', 0, '%s: %f seconds' % (method_name, profile_dict[method_name]))

        except ConflictError:
          raise
        except:
          LOG('SQLCatalog', WARNING, 'could not catalog objects %s with method %s' % (object_list, method_name),
              error=sys.exc_info())
          raise
    finally:
      if not disable_cache:
        disableReadOnlyTransactionCache(self)

  if psyco is not None:
    psyco.bind(_catalogObjectList)

  def beforeUncatalogObject(self, path=None,uid=None):
    """
    Set the path as deleted
    """
    if not self.isIndexable():
      return None

    if uid is None and path is not None:
      uid = self.getUidForPath(path)
    method_name = self.sql_catalog_delete_uid
    if uid is None:
      return None
    if method_name in (None,''):
      # This should exist only if the site is not up to date.
      LOG('ZSQLCatalog.beforeUncatalogObject',0,'The sql_catalog_delete_uid'\
                                                + ' method is not defined')
      return self.uncatalogObject(path=path,uid=uid)
    method = getattr(self, method_name)
    method(uid = uid)

  def uncatalogObject(self, path=None, uid=None):
    """
    Uncatalog and object from the Catalog.

    Note, the uid must be the same as when the object was
    catalogued, otherwise it will not get removed from the catalog

    This method should not raise an exception if the uid cannot
    be found in the catalog.

    XXX Add filter of methods

    """
    if not self.isIndexable():
      return None

    if uid is None and path is not None:
      uid = self.getUidForPath(path)
    methods = self.sql_uncatalog_object
    if uid is None:
      return None
    for method_name in methods:
      # Do not put try/except here, it is required to raise error
      # if uncatalog does not work.
      method = getattr(self, method_name)
      method(uid = uid)

  def catalogTranslationList(self, object_list):
    """Catalog translations.
    """
    method_name = self.sql_catalog_translation_list
    return self.catalogObjectList(object_list, method_id_list = (method_name,),
                                  check_uid=0)

  def deleteTranslationList(self):
    """Delete translations.
    """
    method_name = self.sql_delete_translation_list
    method = getattr(self, method_name)
    try:
      method()
    except ConflictError:
      raise
    except:
      LOG('SQLCatalog', WARNING, 'could not delete translations', error=sys.exc_info())

  def uniqueValuesFor(self, name):
    """ return unique values for FieldIndex name """
    method = getattr(self, self.sql_unique_values)
    return method(column=name)

  def getPaths(self):
    """ Returns all object paths stored inside catalog """
    method = getattr(self, self.sql_catalog_paths)
    return method()

  def getUidForPath(self, path):
    """ Looks up into catalog table to convert path into uid """
    #try:
    if path is None:
      return None
    # Get the appropriate SQL Method
    method = getattr(self, self.sql_getitem_by_path)
    search_result = method(path = path, uid_only=1)
    # If not empty, return first record
    if len(search_result) > 0:
      return long(search_result[0].uid)
    else:
      return None

  def getUidDictForPathList(self, path_list):
    """ Looks up into catalog table to convert path into uid """
    # Get the appropriate SQL Method
    method = getattr(self, self.sql_getitem_by_path)
    path_uid_dict = {}
    try:
      search_result = method(path_list = path_list)
      # If not empty, return first record
      for result in search_result:
        path_uid_dict[result.path] = result.uid
    except ValueError, message:
      # This code is only there for backward compatibility
      # XXX this must be removed one day
      # This means we have the previous zsql method
      # and we must call the method for every path
      for path in path_list:
        search_result = method(path = path)
        if len(search_result) > 0:
          path_uid_dict[path] = search_result[0].uid
    return path_uid_dict

  def getPathDictForUidList(self, uid_list):
    """ Looks up into catalog table to convert uid into path """
    # Get the appropriate SQL Method
    method = getattr(self, self.sql_getitem_by_uid)
    uid_path_dict = {}
    try:
      search_result = method(uid_list = uid_list)
      # If not empty, return first record
      for result in search_result:
        uid_path_dict[result.uid] = result.path
    except ValueError, message:
      # This code is only there for backward compatibility
      # XXX this must be removed one day
      # This means we have the previous zsql method
      # and we must call the method for every path
      for uid in uid_list:
        search_result = method(uid = uid)
        if len(search_result) > 0:
          uid_path_dict[uid] = search_result[0].path
    return uid_path_dict

  def hasPath(self, path):
    """ Checks if path is catalogued """
    return self.getUidForPath(path) is not None

  def getPathForUid(self, uid):
    """ Looks up into catalog table to convert uid into path """
    try:
      if uid is None:
        return None
      try:
        int(uid)
      except ValueError:
        return None
      # Get the appropriate SQL Method
      method = getattr(self, self.sql_getitem_by_uid)
      search_result = method(uid = uid)
      # If not empty return first record
      if len(search_result) > 0:
        return search_result[0].path
      else:
        return None
    except ConflictError:
      raise
    except:
      # This is a real LOG message
      # which is required in order to be able to import .zexp files
      LOG('SQLCatalog', WARNING, "could not find path from uid %s" % (uid,))
      return None

  def getMetadataForUid(self, uid):
    """ Accesses a single record for a given uid """
    if uid is None:
      return None
    # Get the appropriate SQL Method
    method = getattr(self, self.sql_getitem_by_uid)
    brain = method(uid = uid)[0]
    result = {}
    for k in brain.__record_schema__.keys():
      result[k] = getattr(brain,k)
    return result

  def getIndexDataForUid(self, uid):
    """ Accesses a single record for a given uid """
    return self.getMetadataForUid(uid)

  def getMetadataForPath(self, path):
    """ Accesses a single record for a given path """
    try:
      # Get the appropriate SQL Method
      method = getattr(self, self.sql_getitem_by_path)
      brain = method(path = path)[0]
      result = {}
      for k in brain.__record_schema__.keys():
        result[k] = getattr(brain,k)
      return result
    except ConflictError:
      raise
    except:
      # This is a real LOG message
      # which is required in order to be able to import .zexp files
      LOG('SQLCatalog', WARNING,
          "could not find metadata from path %s" % (path,))
      return None

  def getIndexDataForPath(self, path):
    """ Accesses a single record for a given path """
    return self.getMetadataForPath(path)

  def getCatalogMethodIds(self):
    """Find Z SQL methods in the current folder and above
    This function return a list of ids.
    """
    ids={}
    have_id=ids.has_key

    while self is not None:
      if hasattr(self, 'objectValues'):
        for o in self.objectValues(valid_method_meta_type_list):
          if hasattr(o,'id'):
            id=o.id
            if not isinstance(id, str):
              id=id()
            if not have_id(id):
              if hasattr(o,'title_and_id'): o=o.title_and_id()
              else: o=id
              ids[id]=id
      if hasattr(self, 'aq_parent'): self=self.aq_parent
      else: self=None

    ids=map(lambda item: (item[1], item[0]), ids.items())
    ids.sort()
    return ids

  def getSQLCatalogRelatedKeyList(self, key_list=None):
    """
    Return the list of related keys.
    This method can be overidden in order to implement
    dynamic generation of some related keys.
    """
    if key_list is None:
      key_list = []
    # Do not generate dynamic related key for acceptable_keys
    dynamic_key_list = [k for k in key_list \
        if k not in self.getColumnMap().keys()]

    dynamic_list = self.getDynamicRelatedKeyList(dynamic_key_list)
    full_list = list(dynamic_list) + list(self.sql_catalog_related_keys)
    return full_list

  # Compatibililty SQL Sql
  getSqlCatalogRelatedKeyList = getSQLCatalogRelatedKeyList

  def getSQLCatalogScriptableKeyList(self):
    """
    Return the list of scriptable keys.
    """
    return self.sql_catalog_scriptable_keys

  def getTableIndex(self, table):
    """
    Return a map between index and column for a given table
    """
    def _getTableIndex(table):
      table_index = {}
      method = getattr(self, self.sql_catalog_index, '')
      if method in ('', None):
        return {}
      index = list(method(table=table))
      for line in index:
        if table_index.has_key(line.KEY_NAME):
          table_index[line.KEY_NAME].append(line.COLUMN_NAME)
        else:
          table_index[line.KEY_NAME] = [line.COLUMN_NAME,]
      LOG("SQLCatalog.getTableIndex", INFO, "index = %s for table = %s" \
          %(table_index, table))
      return table_index
    return CachingMethod(_getTableIndex, id='SQLCatalog.getTableIndex', \
                         cache_factory='erp5_content_long')(table=table)


  def getIndex(self, table, column_list, all_column_list):
    """
    Return possible index for a column list in a given table
    """
    def _getIndex(table, column_list, all_column_list):
      index_dict = self.getTableIndex(table)
      if isinstance(column_list, str):
        column_list = [column_list,]
      # Get possible that can be used
      possible_index = []
      for index in index_dict.keys():
        index_columns = index_dict[index]
        for column in index_columns:
          if column in column_list:
            if index not in possible_index:
              possible_index.append(index)
      if len(possible_index) == 0:
        return []
      # Get the most suitable index
      for index in possible_index:
        # Make sure all column in index are used by the query
        index_column = index_dict[index]
        for column in index_column:
          if column in column_list or column in all_column_list:
            continue
          else:
            possible_index.remove(index)
      LOG("SQLCatalog.getIndex", INFO, "index = %s for table %s and columns %s" \
          %(possible_index, table, column_list))
      return possible_index
    return CachingMethod(_getIndex, id='SQLCatalog.getIndex', cache_factory='erp5_content_long')\
          (table=table, column_list=column_list, all_column_list=all_column_list)


  def buildSQLQuery(self, query_table='catalog', REQUEST=None,
                          ignore_empty_string=1, query=None, stat__=0, **kw):
    """ Builds a complex SQL query to simulate ZCatalog behaviour """
    # Get search arguments:
    if REQUEST is None and (kw is None or kw == {}):
      # We try to get the REQUEST parameter
      # since we have nothing handy
      try: REQUEST=self.REQUEST
      except AttributeError: pass

    #LOG('SQLCatalog.buildSQLQuery, kw',0,kw)
    # If kw and query are not set, then use REQUEST instead
    if query is None and (kw is None or kw == {}):
      kw = REQUEST

    acceptable_key_map = self.getColumnMap()
    full_text_search_keys = list(self.sql_catalog_full_text_search_keys)
    keyword_search_keys = list(self.sql_catalog_keyword_search_keys)
    topic_search_keys = self.sql_catalog_topic_search_keys
    multivalue_keys = self.sql_catalog_multivalue_keys


    # Compute "sort_index", which is a sort index, or none:
    if kw.has_key('sort-on'):
      sort_index=kw['sort-on']
    elif hasattr(self, 'sort-on'):
      sort_index=getattr(self, 'sort-on')
    elif kw.has_key('sort_on'):
      sort_index=kw['sort_on']
    else: sort_index=None

    # Compute the sort order
    if kw.has_key('sort-order'):
      so=kw['sort-order']
    elif hasattr(self, 'sort-order'):
      so=getattr(self, 'sort-order')
    elif kw.has_key('sort_order'):
      so=kw['sort_order']
    else: so=None

    # We must now turn sort_index into
    # a dict with keys as sort keys and values as sort order
    if isinstance(sort_index, basestring):
      sort_index = [(sort_index, so)]
    elif not isinstance(sort_index, (list, tuple)):
      sort_index = None

    # Rebuild keywords to behave as new style query (_usage='toto:titi' becomes {'toto':'titi'})
    new_kw = {}
    usage_len = len('_usage')
    for k, v in kw.items():
      if k.endswith('_usage'):
        new_k = k[0:-usage_len]
        if not new_kw.has_key(new_k):
          new_kw[new_k] = {}
        if not isinstance(new_kw[new_k], dict):
          new_kw[new_k] = {'query': new_kw[new_k]}
        split_v = v.split(':')
        new_kw[new_k] = {split_v[0]: split_v[1]}
      else:
        if not new_kw.has_key(k):
          new_kw[k] = v
        else:
          new_kw[k]['query'] = v
    kw = new_kw

    # Initialise Scriptable Dict
    scriptable_key_dict = {}
    for t in self.sql_catalog_scriptable_keys:
      t = t.split('|')
      key = t[0].strip()
      method_id = t[1].strip()
      scriptable_key_dict[key] = method_id

    # Build the list of Queries and ComplexQueries
    query_dict = {}
    key_list = [] # the list of column keys
    key_alias_dict = {}
    query_group_by_list = None # Useful to keep a default group_by passed by scriptable keys
    query_related_table_map_dict = {}
    if query is not None:
      kw ['query'] = query
    for key in kw.keys():
      if key not in RESERVED_KEY_LIST:
        value = kw[key]
        current_query = None
        new_query_dict = {}
        if isinstance(value, (Query, ComplexQuery)):
          current_query = value
        elif scriptable_key_dict.has_key(key):
          # Turn this key into a query by invoking a script
          method = getattr(self, scriptable_key_dict[key])
          current_query = method(value) # May return None
          if hasattr(current_query, 'order_by'): query_group_by_list = current_query.order_by
        else:
          if isinstance(value, dict):
            for value_key in value.keys():
              if value_key == 'query':
                new_query_dict[key] = value['query']
              else:
                new_query_dict[value_key] = value[value_key]
          else:
            new_query_dict[key] = value
          current_query = Query(**new_query_dict)
        if current_query is not None:
          query_dict[key] = current_query
          key_list.extend(current_query.getSQLKeyList())
          query_related_table_map_dict.update(current_query.getRelatedTableMapDict())

    # if we have a sort index, we must take it into account to get related
    # keys.
    if sort_index:
      related_key_kw = dict(kw)
      for sort_info in sort_index:
        sort_key = sort_info[0]
        if sort_key not in key_list:
          key_list.append(sort_key)

    related_tuples = self.getSQLCatalogRelatedKeyList(key_list=key_list)

    # Define related maps
    # each tuple from `related_tuples` has the form (key,
    # 'table1,table2,table3/column/where_expression')
    related_keys = {}
    related_method = {}
    related_table_map = {}
    related_column = {}
    related_table_list = {}
    table_rename_index = 0
    related_methods = {} # related methods which need to be used
    for t in related_tuples:
      t_tuple = t.split('|')
      key = t_tuple[0].strip()
      if key in key_list:
        if ignore_empty_string \
            and kw.get(key, '') in ('', [], ()):
              # we don't ignore 0
          continue
        join_tuple = t_tuple[1].strip().split('/')
        related_keys[key] = None
        method_id = join_tuple[2]
        table_list = tuple(join_tuple[0].split(','))
        related_method[key] = method_id
        related_table_list[key] = table_list
        related_column[key] = join_tuple[1]
        # Check if some aliases where specified in queries
        map_list = query_related_table_map_dict.get(key,None)
        # Rename tables to prevent conflicts
        if not related_table_map.has_key((table_list,method_id)):
          if map_list is None:
            map_list = []
            for table_id in table_list:
              map_list.append((table_id,
                 "related_%s_%s" % (table_id, table_rename_index))) # We add an index in order to alias tables in the join
              table_rename_index += 1 # and prevent name conflicts
          related_table_map[(table_list,method_id)] = map_list

    # We take additional parameters from the REQUEST
    # and give priority to the REQUEST
    if REQUEST is not None:
      for key in acceptable_key_map.iterkeys():
        if REQUEST.has_key(key):
          # Only copy a few keys from the REQUEST
          if key in self.sql_catalog_request_keys:
            kw[key] = REQUEST[key]

    def getNewKeyAndUpdateVariables(key):
      key_is_acceptable = key in acceptable_key_map # Only calculate once
      key_is_related = key in related_keys
      new_key = None
      if key_is_acceptable or key_is_related:
        if key_is_related: # relation system has priority (ex. security_uid)
          # We must rename the key
          method_id = related_method[key]
          table_list = related_table_list[key]
          if not related_methods.has_key((table_list,method_id)):
            related_methods[(table_list,method_id)] = 1
          # Prepend renamed table name
          new_key = "%s.%s" % (related_table_map[(table_list,method_id)][-1][-1],
                               related_column[key])
        elif key_is_acceptable:
          if key.find('.') < 0:
            # if the key is only used by one table, just append its name
            if len(acceptable_key_map[key]) == 1 :
              new_key = '%s.%s' % (acceptable_key_map[key][0], key)
            # query_table specifies what table name should be used by default
            elif query_table and \
                '%s.%s' % (query_table, key) in acceptable_key_map:
              new_key = '%s.%s' % (query_table, key)
            elif key == 'uid':
              # uid is always ambiguous so we can only change it here
              new_key = 'catalog.uid'
          else:
            new_key = key
          if new_key is not None:
            # Add table to table dict, we use catalog by default
            from_table_dict[acceptable_key_map[new_key][0]] = acceptable_key_map[new_key][0]
      key_alias_dict[key] = new_key
      return new_key

    where_expression_list = []
    select_expression_list = []
    group_by_expression_list = []
    where_expression = ''
    select_expression = ''
    group_by_expression = ''

    from_table_dict = {'catalog' : 'catalog'} # Always include catalog table
    if len(kw):
      if kw.has_key('select_expression'):
        select_expression_list.append(kw['select_expression'])
      if kw.has_key('group_by_expression'):
        group_by_expression_list.append(kw['group_by_expression'])
      # Grouping
      group_by_list = kw.get('group_by', query_group_by_list)
      if type(group_by_list) is type('a'): group_by_list = [group_by_list]
      if group_by_list is not None:
        try:
          for key in group_by_list:
            new_key = getNewKeyAndUpdateVariables(key)
            group_by_expression_list.append(new_key)
        except ConflictError:
          raise
        except:
          LOG('SQLCatalog', WARNING, 'buildSQLQuery could not build the new group by expression', error=sys.exc_info())
          group_by_expression = ''
      if len(group_by_expression_list)>0:
        group_by_expression = ','.join(group_by_expression_list)
        group_by_expression = str(group_by_expression)

    sort_on = None
    sort_key_list = []
    if sort_index is not None:
      new_sort_index = []
      for sort in sort_index:
        if len(sort) == 2:
          # Try to analyse expressions of the form "title AS unsigned"
          sort_key_list = sort[0].split()
          if len(sort_key_list) == 3:
            sort_key = sort_key_list[0]
            sort_type = sort_key_list[2]
          elif len(sort_key_list):
            sort_key = sort_key_list[0]
            sort_type = None
          else:
            sort_key = sort[0]
            sort_type = None
          new_sort_index.append((sort_key, sort[1], sort_type))
        elif len(sort) == 3:
          new_sort_index.append(sort)
      sort_index = new_sort_index
      try:
        new_sort_index = []
        for (original_key, so, as_type) in sort_index:
          key = getNewKeyAndUpdateVariables(original_key)
          if key is not None:
            sort_key_list.append(key)
            if as_type == 'int':
              key = 'CAST(%s AS SIGNED)' % key
            elif as_type:
              key = 'CAST(%s AS %s)' % (key, as_type) # Different casts are possible
            if so in ('descending', 'reverse', 'DESC'):
              new_sort_index.append('%s DESC' % key)
            else:
              new_sort_index.append('%s' % key)
          else:
            LOG('SQLCatalog', WARNING, 'buildSQLQuery could not build sort '
                'index (%s -> %s)' % (original_key, key))
        sort_index = join(new_sort_index,',')
        sort_on = str(sort_index)
      except ConflictError:
        raise
      except:
        LOG('SQLCatalog', WARNING, 'buildSQLQuery could not build the new sort index', error=sys.exc_info())
        sort_on = ''
        sort_key_list = []

    for key in key_list:
      if not key_alias_dict.has_key(key):
        getNewKeyAndUpdateVariables(key)
    if len(query_dict):
      for key, query in query_dict.items():
        query_result = query.asSQLExpression(key_alias_dict=key_alias_dict,
                                    full_text_search_keys=full_text_search_keys,
                                    keyword_search_keys=keyword_search_keys,
                                    ignore_empty_string=ignore_empty_string,
                                    stat__=stat__)
        if query_result['where_expression'] not in ('',None):
          where_expression_list.append(query_result['where_expression'])
        select_expression_list.extend(query_result['select_expression_list'])

    # Calculate extra where_expression based on required joins
    for k, tid in from_table_dict.items():
      if k != query_table:
        where_expression_list.append('%s.uid = %s.uid' % (query_table, tid))
    # Calculate extra where_expressions based on related definition
    for (table_list, method_id) in related_methods.keys():
      related_method = getattr(self, method_id, None)
      if related_method is not None:
        table_id = {'src__' : 1} # Return query source, do not evaluate
        table_id['query_table'] = query_table
        table_index = 0
        for t_tuple in related_table_map[(table_list,method_id)]:
          table_id['table_%s' % table_index] = t_tuple[1] # table_X is set to mapped id
          from_table_dict[t_tuple[1]] = t_tuple[0]
          table_index += 1
        where_expression_list.append(related_method(**table_id))
    # Concatenate expressions
    if kw.get('where_expression',None) not in (None,''):
      where_expression_list.append(kw['where_expression'])
    if len(where_expression_list)>1:
      where_expression_list = ['(%s)' % x for x in where_expression_list]
    where_expression = join(where_expression_list, ' AND ')
    select_expression= join(select_expression_list,',')

    limit_expression = kw.get('limit', None)
    if isinstance(limit_expression, (list, tuple)):
      limit_expression = '%s,%s' % (limit_expression[0], limit_expression[1])
    elif limit_expression is not None:
      limit_expression = str(limit_expression)

    # force index if exists when doing sort as mysql doesn't manage them efficiently
    if len(sort_key_list) > 0:
      index_from_table = {}
      # first group columns from a same table
      for key in sort_key_list:
        try:
          related_table, column = key.split('.')
        except ValueError:
          # key is not of the form table.column
          # so get table from dict
          if len(from_table_dict) != 1:
            continue
          column = key
          related_table = from_table_dict.keys()[0]

        table = from_table_dict[related_table]
        # Check if it's a column for which we want to specify index
        index_columns = getattr(self, 'sql_catalog_index_on_order_keys', [])
        sort_column = '%s.%s' %(table, column)
        if not sort_column in index_columns:
          continue
        # Group columns
        if not index_from_table.has_key(table):
          index_from_table[table] = [column,]
        else:
          index_from_table[table].append(column)
      # second ask index
      for table in index_from_table.keys():
        available_index_list = self.getIndex(table, index_from_table[table], key_list)
        if len(available_index_list) > 0:
          # tell mysql to use these index
          table = from_table_dict.pop(related_table)
          index_list_string = ""
          for index in available_index_list:
            if len(index_list_string) == 0:
              index_list_string += "%s" %index
            else:
              index_list_string += ", %s" %index
          table_with_index =  "%s use index(%s)"  %(related_table, index_list_string)
          from_table_dict[table_with_index] = table

    # Use a dictionary at the moment.
    return { 'from_table_list' : from_table_dict.items(),
             'order_by_expression' : sort_on,
             'where_expression' : where_expression,
             'limit_expression' : limit_expression,
             'select_expression': select_expression,
             'group_by_expression' : group_by_expression}

  # Compatibililty SQL Sql
  buildSqlQuery = buildSQLQuery

  def queryResults(self, sql_method, REQUEST=None, used=None, src__=0, build_sql_query_method=None, **kw):
    """ Returns a list of brains from a set of constraints on variables """
    if build_sql_query_method is None:
      build_sql_query_method = self.buildSQLQuery
    query = build_sql_query_method(REQUEST=REQUEST, **kw)
    kw['where_expression'] = query['where_expression']
    kw['sort_on'] = query['order_by_expression']
    kw['from_table_list'] = query['from_table_list']
    kw['limit_expression'] = query['limit_expression']
    kw['select_expression'] = query['select_expression']
    kw['group_by_expression'] = query['group_by_expression']
    # Return the result

    #LOG('acceptable_keys',0,'acceptable_keys: %s' % str(acceptable_keys))
    #LOG('acceptable_key_map',0,'acceptable_key_map: %s' % str(acceptable_key_map))
    #LOG('queryResults',0,'kw: %s' % str(kw))
    #LOG('queryResults',0,'from_table_list: %s' % str(query['from_table_list']))
    return sql_method(src__=src__, **kw)

  def searchResults(self, REQUEST=None, used=None, **kw):
    """ Returns a list of brains from a set of constraints on variables """
    # The used argument is deprecated and is ignored
    method = getattr(self, self.sql_search_results)
    return self.queryResults(method, REQUEST=REQUEST, used=used, **kw)

  __call__ = searchResults

  def countResults(self, REQUEST=None, used=None, stat__=1, **kw):
    """ Returns the number of items which satisfy the where_expression """
    # Get the search method
    method = getattr(self, self.sql_count_results)
    return self.queryResults(method, REQUEST=REQUEST, used=used, stat__=stat__, **kw)

  def recordObjectList(self, path_list, catalog=1):
    """
      Record the path of an object being catalogged or uncatalogged.
    """
    method = getattr(self, self.sql_record_object_list)
    method(path_list=path_list, catalog=catalog)

  def deleteRecordedObjectList(self, uid_list=()):
    """
      Delete all objects which contain any path.
    """
    method = getattr(self, self.sql_delete_recorded_object_list)
    method(uid_list=uid_list)

  def readRecordedObjectList(self, catalog=1):
    """
      Read objects. Note that this might not return all objects since ZMySQLDA limits the max rows.
    """
    method = getattr(self, self.sql_read_recorded_object_list)
    return method(catalog=catalog)

  # Filtering
  def manage_editFilter(self, REQUEST=None, RESPONSE=None, URL1=None):
    """
    This methods allows to set a filter on each zsql method called,
    so we can test if we should or not call a zsql method, so we can
    increase a lot the speed.
    """
    if withCMF:
      method_id_list = [zsql_method.id for zsql_method in self.getFilterableMethodList()]

      # Remove unused filters.
      for id in self.filter_dict.keys():
        if id not in method_id_list:
          del self.filter_dict[id]

      for id in method_id_list:
        # We will first look if the filter is activated
        if not self.filter_dict.has_key(id):
          self.filter_dict[id] = PersistentMapping()
          self.filter_dict[id]['filtered'] = 0
          self.filter_dict[id]['type'] = []
          self.filter_dict[id]['expression'] = ""
          self.filter_dict[id]['expression_cache_key'] = "portal_type"

        if REQUEST.has_key('%s_box' % id):
          self.filter_dict[id]['filtered'] = 1
        else:
          self.filter_dict[id]['filtered'] = 0

        if REQUEST.has_key('%s_expression' % id):
          expression = REQUEST['%s_expression' % id]
          if expression == "":
            self.filter_dict[id]['expression'] = ""
            self.filter_dict[id]['expression_instance'] = None
          else:
            expr_instance = Expression(expression)
            self.filter_dict[id]['expression'] = expression
            self.filter_dict[id]['expression_instance'] = expr_instance
        else:
          self.filter_dict[id]['expression'] = ""
          self.filter_dict[id]['expression_instance'] = None

        if REQUEST.has_key('%s_type' % id):
          list_type = REQUEST['%s_type' % id]
          if isinstance(list_type, str):
            list_type = [list_type]
          self.filter_dict[id]['type'] = list_type
        else:
          self.filter_dict[id]['type'] = []

        if REQUEST.has_key('%s_expression_cache_key' % id):
          expression_cache_key = REQUEST['%s_expression_cache_key' % id]
          if expression_cache_key == "":
            self.filter_dict[id]['expression_cache_key'] = expression_cache_key
          else:
            self.filter_dict[id]['expression_cache_key'] = ""
        else:
          self.filter_dict[id]['expression_cache_key'] = ""

    if RESPONSE and URL1:
      RESPONSE.redirect(URL1 + '/manage_catalogFilter?manage_tabs_message=Filter%20Changed')

  def isMethodFiltered(self, method_name):
    """
    Returns 1 if the method is already filtered,
    else it returns 0
    """
    if withCMF:
      # Reset Filtet dict
      if getattr(aq_base(self), 'filter_dict', None) is None:
        self.filter_dict = PersistentMapping()
        return 0
      try:
        return self.filter_dict[method_name]['filtered']
      except KeyError:
        return 0
    return 0

  def getExpression(self, method_name):
    """ Get the filter expression text for this method.
    """
    if withCMF:
      if getattr(aq_base(self), 'filter_dict', None) is None:
        self.filter_dict = PersistentMapping()
        return ""
      try:
        return self.filter_dict[method_name]['expression']
      except KeyError:
        return ""
    return ""

  def getExpressionCacheKey(self, method_name):
    """ Get the key string which is used to cache results
        for the given expression.
    """
    if withCMF:
      if getattr(aq_base(self), 'filter_dict', None) is None:
        self.filter_dict = PersistentMapping()
        return ""
      try:
        return self.filter_dict[method_name]['expression_cache_key']
      except KeyError:
        return ""
    return ""

  def getExpressionInstance(self, method_name):
    """ Get the filter expression instance for this method.
    """
    if withCMF:
      if getattr(aq_base(self), 'filter_dict', None) is None:
        self.filter_dict = PersistentMapping()
        return None
      try:
        return self.filter_dict[method_name]['expression_instance']
      except KeyError:
        return None
    return None

  def isPortalTypeSelected(self, method_name, portal_type):
    """ Returns true if the portal type is selected for this method.
    """
    if withCMF:
      if getattr(aq_base(self), 'filter_dict', None) is None:
        self.filter_dict = PersistentMapping()
        return 0
      try:
        return portal_type in (self.filter_dict[method_name]['type'])
      except KeyError:
        return 0
    return 0

  def getFilteredPortalTypeList(self, method_name):
    """ Returns the list of portal types which define
        the filter.
    """
    if withCMF:
      if getattr(aq_base(self), 'filter_dict', None) is None:
        self.filter_dict = PersistentMapping()
        return []
      try:
        return self.filter_dict[method_name]['type']
      except KeyError:
        return []
    return []

  def getFilterableMethodList(self):
    """
    Returns only zsql methods wich catalog or uncatalog objets
    """
    method_dict = {}
    if withCMF:
      methods = getattr(self,'sql_catalog_object',()) + \
                getattr(self,'sql_uncatalog_object',()) + \
                getattr(self,'sql_update_object',()) + \
                getattr(self,'sql_catalog_object_list',())
      for method_id in methods:
        method_dict[method_id] = 1
    method_list = map(lambda method_id: getattr(self, method_id, None), method_dict.keys())
    return filter(lambda method: method is not None, method_list)

  def getExpressionContext(self, ob):
      '''
      An expression context provides names for TALES expressions.
      '''
      if withCMF:
        data = {
            'here':         ob,
            'container':    aq_parent(aq_inner(ob)),
            'nothing':      None,
            #'root':         ob.getPhysicalRoot(),
            #'request':      getattr( ob, 'REQUEST', None ),
            #'modules':      SecureModuleImporter,
            #'user':         getSecurityManager().getUser(),
            'isDelivery':   ob.isDelivery, # XXX
            'isMovement':   ob.isMovement, # XXX
            'isPredicate':  ob.isPredicate, # XXX
            'isDocument':   ob.isDocument, # XXX
            'isInventory':  ob.isInventory, # XXX
            'isInventoryMovement': ob.isInventoryMovement, # XXX
            }
        return getEngine().getContext(data)


Globals.default__class_init__(Catalog)

class CatalogError(Exception): pass

