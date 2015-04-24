# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SARL. All Rights Reserved.
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

from Persistence import Persistent, PersistentMapping
import Acquisition
import ExtensionClass
import OFS.History
from App.class_init import default__class_init__ as InitializeClass
from App.special_dtml import DTMLFile
from thread import allocate_lock, get_ident
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.SimpleObjectPolicies import ContainerAssertions
from BTrees.OIBTree import OIBTree
from App.config import getConfiguration
from BTrees.Length import Length
from Shared.DC.ZRDB.TM import TM

from Acquisition import aq_parent, aq_inner, aq_base
from zLOG import LOG, WARNING, INFO, TRACE, ERROR
from ZODB.POSException import ConflictError
from Products.PythonScripts.Utility import allow_class

import time
import sys
import urllib
import string
import pprint
import re
import warnings
from contextlib import contextmanager
from cStringIO import StringIO
from xml.dom.minidom import parse
from xml.sax.saxutils import escape, quoteattr
import os
from hashlib import md5

from interfaces.query_catalog import ISearchKeyCatalog
from zope.interface.verify import verifyClass
from zope.interface import implements

from SearchText import isAdvancedSearchText, dequote

# Try to import ActiveObject in order to make SQLCatalog active
try:
  from Products.CMFActivity.ActiveObject import ActiveObject
except ImportError:
  ActiveObject = ExtensionClass.Base

try:
  from Products.CMFCore.Expression import Expression
  from Products.PageTemplates.Expressions import getEngine
  from Products.CMFCore.utils import getToolByName
  new_context_search = re.compile(r'\bcontext\b').search
  withCMF = 1
except ImportError:
  withCMF = 0

try:
  import psyco
except ImportError:
  psyco = None

@contextmanager
def noReadOnlyTransactionCache():
  yield
try:
  from Products.ERP5Type.Cache import \
    readOnlyTransactionCache
except ImportError:
  LOG('SQLCatalog', WARNING, 'Count not import caching_instance_method, expect slowness.')
  readOnlyTransactionCache = noReadOnlyTransactionCache

try:
  from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
except ImportError:
  LOG('SQLCatalog', WARNING, 'Count not import getTransactionalVariable, expect slowness.')
  def getTransactionalVariable():
    return {}

def getInstanceID(instance):
  # XXX: getPhysicalPath is overkill for a unique cache identifier.
  # What I would like to use instead of it is:
  #   (self._p_jar.db().database_name, self._p_oid)
  # but database_name is not unique in at least ZODB 3.4 (Zope 2.8.8).
  return instance.getPhysicalPath()

def generateCatalogCacheId(method_id, self, *args, **kwd):
  return str((method_id, self.getCacheSequenceNumber(), getInstanceID(self),
    args, kwd))

class transactional_cache_decorator:
  """
    Implements singleton-style caching.
    Wrapped method must have no parameters (besides "self").
  """
  def __init__(self, cache_id):
    self.cache_id = cache_id

  def __call__(self, method):
    def wrapper(wrapped_self):
      transactional_cache = getTransactionalVariable()
      cache_id = str((self.cache_id,
        wrapped_self.getCacheSequenceNumber(),
        getInstanceID(wrapped_self),
      ))
      try:
        result = transactional_cache[cache_id]
      except KeyError:
        result = transactional_cache[cache_id] = method(wrapped_self)
      return result
    return wrapper

list_type_list = list, tuple, set, frozenset
try:
  from ZPublisher.HTTPRequest import record
except ImportError:
  dict_type_list = (dict, )
else:
  dict_type_list = (dict, record)


UID_BUFFER_SIZE = 300
OBJECT_LIST_SIZE = 300 # XXX 300 is arbitrary value of catalog object list
MAX_PATH_LEN = 255
RESERVED_KEY_LIST = ('where_expression', 'sort-on', 'sort_on', 'sort-order', 'sort_order', 'limit',
                     'format', 'search_mode', 'operator', 'selection_domain', 'selection_report',
                     'extra_key_list', )

valid_method_meta_type_list = ('Z SQL Method', 'LDIF Method', 'Script (Python)') # Nicer

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

class DummyDict(dict):
  def __setitem__(self, key, value):
    pass

class LazyIndexationParameterList(tuple):
  def __new__(cls, document_list, attribute, global_cache):
    self = super(LazyIndexationParameterList, cls).__new__(cls)
    self._document_list = document_list
    self._attribute = attribute
    self._global_cache = global_cache
    return self

  def __getitem__(self, index):
    document = self._document_list[index]
    attribute = self._attribute
    global_cache_key = (document.uid, attribute)
    global_cache = self._global_cache
    if global_cache_key in global_cache:
      value = global_cache[global_cache_key]
    else:
      value = getattr(document, attribute, None)
      if callable(value):
        try:
          value = value()
        except ConflictError:
          raise
        except Exception:
          LOG('SQLCatalog', WARNING,
            'Failed to call method %s on %r' % (attribute, document),
            error=True,
          )
          value = None
      global_cache[global_cache_key] = value
    return value

  def __iter__(self):
    for index in xrange(len(self)):
      yield self[index]

  def __len__(self):
    return len(self._document_list)

  def __repr__(self):
    return '<%s(%i documents, %r) at %x>' % (self.__class__.__name__,
      len(self), self._attribute, id(self))

ContainerAssertions[LazyIndexationParameterList] = 1

related_key_warned_column_set = set()

class Catalog(Folder,
              Persistent,
              Acquisition.Implicit,
              ActiveObject,
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

 """

  implements(ISearchKeyCatalog)


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
    { 'id': 'sql_catalog_search_keys',
      'title': 'Search Key Mappings',
      'description': 'A list of Search Key mappings',
      'type': 'lines',
      'mode': 'w' },
    { 'id'      : 'sql_catalog_keyword_search_keys',
      'description' : 'Columns which should be considered as keyword search',
      'type'    : 'multiple selection',
      'select_variable' : 'getColumnIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_datetime_search_keys',
      'description' : 'Columns which should be considered as datetime search',
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
    { 'id': 'sql_catalog_role_keys',
      'title': 'Role keys',
      'description': 'Columns which should be used to map a monovalued role',
      'type': 'lines',
      'mode': 'w' },
    { 'id': 'sql_catalog_local_role_keys',
      'title': 'Local Role keys',
      'description': 'Columns which should be used to map' \
                      'a monovalued local role',
      'type': 'lines',
      'mode': 'w' },
    { 'id': 'sql_catalog_security_uid_columns',
      'title': 'Security Uid Columns',
      'description': 'A list of mappings "local_roles_group_id | security_uid_column"'
                     ' local_roles_group_id will be the name of a local roles'
                     ' group, and security_uid_column is the corresponding'
                     ' column in catalog table',
      'type': 'lines',
      'mode': 'w' },
    { 'id': 'sql_catalog_table_vote_scripts',
      'title': 'Table vote scripts',
      'description': 'Scripts helping column mapping resolution',
      'type': 'multiple selection',
      'select_variable' : 'getPythonMethodIds',
      'mode': 'w' },
    { 'id': 'sql_catalog_raise_error_on_uid_check',
      'title': 'Raise error on UID check',
      'description': 'Boolean used to tell if we raise error when uid check fail',
      'type': 'boolean',
      'default' : True,
      'mode': 'w' },

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
  sql_catalog_search_keys = ()
  sql_catalog_keyword_search_keys =  ()
  sql_catalog_datetime_search_keys = ()
  sql_catalog_full_text_search_keys = ()
  sql_catalog_request_keys = ()
  sql_search_result_keys = ()
  sql_catalog_topic_search_keys = ()
  sql_catalog_multivalue_keys = ()
  sql_catalog_index_on_order_keys = ()
  sql_catalog_related_keys = ()
  sql_catalog_scriptable_keys = ()
  sql_catalog_role_keys = ()
  sql_catalog_local_role_keys = ()
  sql_catalog_security_uid_columns = (' | security_uid',)
  sql_catalog_table_vote_scripts = ()
  sql_catalog_raise_error_on_uid_check = True

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

  _cache_sequence_number = 0

  def __init__(self, id, title='', container=None):
    if container is not None:
      self=self.__of__(container)
    self.id=id
    self.title=title
    self.schema = {}  # mapping from attribute name to column
    self.names = {}   # mapping from column to attribute name
    self.indexes = {}   # empty mapping
    self.filter_dict = PersistentMapping()

  def getCacheSequenceNumber(self):
    return self._cache_sequence_number

  def _clearCaches(self):
    self._cache_sequence_number += 1

  def getSQLCatalogRoleKeysList(self):
    """
    Return the list of role keys.
    """
    role_key_dict = {}
    for role_key in self.sql_catalog_role_keys:
      role, column = role_key.split('|')
      role_key_dict[role.strip()] = column.strip()
    return role_key_dict.items()

  def getSQLCatalogSecurityUidGroupsColumnsDict(self):
    """
    Return a mapping of local_roles_group_id name to the name of the column
    storing corresponding security_uid.
    The default mappiny is {'': 'security_uid'}
    """
    local_roles_group_id_dict = {}
    for local_roles_group_id_key in self.sql_catalog_security_uid_columns:
      local_roles_group_id, column = local_roles_group_id_key.split('|')
      local_roles_group_id_dict[local_roles_group_id.strip()] = column.strip()
    return local_roles_group_id_dict

  def getSQLCatalogLocalRoleKeysList(self):
    """
    Return the list of local role keys.
    """
    local_role_key_dict = {}
    for role_key in self.sql_catalog_local_role_keys:
      role, column = role_key.split('|')
      local_role_key_dict[role.strip()] = column.strip()
    return local_role_key_dict.items()

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
    property_list.sort(key=lambda x: x[0])
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
      filter_list.sort(key=lambda x: x[0])
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
    with open(file) as f:
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

  def _clearSubjectCache(self):
    self.subject_set_uid_dict = OIBTree()
    self.subject_set_uid_index = None

  security.declarePrivate('getSecurityUidDict')
  def getSecurityUidDict(self, wrapped_object):
    """
    returns a tuple with a dict of security uid by local group id, and a tuple
    containing optimised_roles_and_users that might have been created.
    """
    if getattr(aq_base(self), 'security_uid_dict', None) is None:
      self._clearSecurityCache()

    optimised_roles_and_users = []
    local_roles_group_id_to_security_uid_mapping = {}

    # Get security information
    security_uid = None
    for key in wrapped_object.getLocalRolesGroupIdDict().iteritems():
      local_roles_group_id, allowed_roles_and_users = key
      allowed_roles_and_users = tuple(sorted(allowed_roles_and_users))
      if self.security_uid_dict.has_key(key):
        local_roles_group_id_to_security_uid_mapping[local_roles_group_id] \
                = self.security_uid_dict[key]
      elif self.security_uid_dict.has_key(allowed_roles_and_users)\
           and not local_roles_group_id:
        # This key is present in security_uid_dict without
        # local_roles_group_id, it has been inserted before
        # local_roles_group_id were introduced.
        local_roles_group_id_to_security_uid_mapping[local_roles_group_id] = \
          self.security_uid_dict[allowed_roles_and_users]
      else:
        if not security_uid:
          getTransactionalVariable().pop('getSecurityUidDictAndRoleColumnDict',
                                         None)
          id_tool = getattr(self.getPortalObject(), 'portal_ids', None)
          # We must keep compatibility with existing sites
          security_uid = getattr(self, 'security_uid_index', None)
          if security_uid is None:
            security_uid = 0
          # At some point, it was a Length
          elif isinstance(security_uid, Length):
            security_uid = security_uid()
        # If the id_tool is there, it is better to use it, it allows
        # to create many new security uids by the same time
        # because with this tool we are sure that we will have 2 different
        # uids if two instances are doing this code in the same time
        security_uid += 1
        if id_tool is not None:
          security_uid = int(id_tool.generateNewId(id_generator='uid',
              id_group='security_uid_index', default=security_uid))
        else:
          self.security_uid_index = security_uid

        self.security_uid_dict[key] = security_uid
        local_roles_group_id_to_security_uid_mapping[local_roles_group_id]\
            = security_uid

        # If some optimised_roles_and_users are returned by this method it
        # means that new entries will have to be added to roles_and_users table.
        for user in allowed_roles_and_users:
          optimised_roles_and_users.append((security_uid, local_roles_group_id, user))

    return (local_roles_group_id_to_security_uid_mapping, optimised_roles_and_users)

  def getRoleAndSecurityUidList(self):
    """
      Return a list of 3-tuples, suitable for direct use in a zsqlmethod.
      Goal: make it possible to regenerate a table containing this data.
    """
    result = []
    for role_list, security_uid in getattr(
            aq_base(self), 'security_uid_dict', {}).iteritems():
      if role_list:
        if isinstance(role_list[-1], tuple):
          local_role_group_id, role_list = role_list
        else:
          local_role_group_id = ''
        result += [(local_role_group_id, role, security_uid)
                  for role in role_list]
    return result

  security.declarePrivate('getSubjectSetUid')
  def getSubjectSetUid(self, wrapped_object):
    """
    Cache a uid for each unique subject tuple.
    Return a tuple with a subject uid (string) and a new subject tuple
    if not exist already.
    """
    getSubjectList = getattr(wrapped_object, 'getSubjectList', None)
    if getSubjectList is None:
      return (None, None)
    # Get subject information
    # XXX if more collation is available, we can have smaller number of
    # unique subject sets.
    subject_list = tuple(sorted({(x or '').lower() for x in getSubjectList()}))
    if not subject_list:
      return (None, None)
    # Make sure no duplicates
    if getattr(aq_base(self), 'subject_set_uid_dict', None) is None:
      self._clearSubjectCache()
    elif self.subject_set_uid_dict.has_key(subject_list):
      return (self.subject_set_uid_dict[subject_list], None)
    # If the id_tool is there, it is better to use it, it allows
    # to create many new subject uids by the same time
    # because with this tool we are sure that we will have 2 different
    # uids if two instances are doing this code in the same time
    id_tool = getattr(self.getPortalObject(), 'portal_ids', None)
    if id_tool is not None:
      default = 1
      # We must keep compatibility with existing sites
      previous_subject_set_uid = getattr(self, 'subject_set_uid_index', None)
      if previous_subject_set_uid is not None:
        default = previous_subject_set_uid
      subject_set_uid = int(id_tool.generateNewId(id_generator='uid',
          id_group='subject_set_uid_index', default=default))
    else:
      previous_subject_set_uid = getattr(self, 'subject_set_uid_index', None)
      if previous_subject_set_uid is None:
        previous_subject_set_uid = 0
      subject_set_uid = previous_subject_set_uid + 1
      self.subject_set_uid_index = subject_set_uid
    self.subject_set_uid_dict[subject_list] = subject_set_uid
    return (subject_set_uid, subject_list)

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
        raise

    # Reserved uids have been removed.
    self.clearReserved()

    id_tool = getattr(self.getPortalObject(), 'portal_ids', None)
    if id_tool is None:
      # Add a dummy item so that SQLCatalog will not use existing uids again.
      self.insertMaxUid()

    self._clearSecurityCache()
    self._clearSubjectCache()
    self._clearCaches()

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

  def getRecordForUid(self, uid):
    """
    Get an object by UID
    Note: brain is defined in Z SQL Method object
    """
    # this method used to be __getitem__(self, uid) but was found to hurt more
    # than it helped: It would be inadvertently called by
    # (un)restrictedTraverse and if there was any error in rendering the SQL
    # expression or contacting the database, an error different from KeyError
    # would be raised, causing confusion.
    # It could also have a performance impact for traversals to objects in
    # the acquisition context on Zope 2.12 even when it didn't raise a weird
    # error.
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
    result_list = []
    try:
      method_name = self.sql_catalog_schema
      method = getattr(self, method_name)
      search_result = method(table=table)
      for c in search_result:
        result_list.append(c.Field)
    except ConflictError:
      raise
    except:
      LOG('SQLCatalog', WARNING, '_getCatalogSchema failed with the method %s' % method_name, error=sys.exc_info())
      pass
    return tuple(result_list)

  @transactional_cache_decorator('SQLCatalog.getColumnIds')
  def _getColumnIds(self):
    keys = set()
    add_key = keys.add
    for table in self.getCatalogSearchTableIds():
      field_list = self._getCatalogSchema(table=table)
      for field in field_list:
        add_key(field)
        add_key('%s.%s' % (table, field))  # Is this inconsistent ?
    for related in self.getSQLCatalogRelatedKeyList():
      related_tuple = related.split('|')
      add_key(related_tuple[0].strip())
    for scriptable in self.getSQLCatalogScriptableKeyList():
      scriptable_tuple = scriptable.split('|')
      add_key(scriptable_tuple[0].strip())
    return sorted(keys)

  def getColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids
    """
    return self._getColumnIds()[:]

  @transactional_cache_decorator('SQLCatalog.getColumnMap')
  def getColumnMap(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids
    """
    result = {}
    for table in self.getCatalogSearchTableIds():
      for field in self._getCatalogSchema(table=table):
        result.setdefault(field, []).append(table)
        result.setdefault('%s.%s' % (table, field), []).append(table) # Is this inconsistent ?
    return result

  @transactional_cache_decorator('SQLCatalog.getResultColumnIds')
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

  @transactional_cache_decorator('SQLCatalog.getSortColumnIds')
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
          self._max_uid = Length(1)
        uid_list = id_tool.generateNewIdList(id_generator='uid', id_group='catalog_uid',
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
        instance_id = md5(str(random_factor_list)).hexdigest()
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
        if self._max_uid is None:
          self._max_uid = Length(1)
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

  def manage_catalogReindex(self, REQUEST, RESPONSE, URL1, urls=None):
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
      return

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

    # This dict will store uids and objects which are verified below.
    # The purpose is to prevent multiple objects from having the same
    # uid inside object_list.
    assigned_uid_dict = {}

    for object in object_list:
      uid = getattr(aq_base(object), 'uid', None)
      # Several Tool objects have uid=0 (not 0L) from the beginning, but
      # we need an unique uid for each object.
      if uid is None or isinstance(uid, int) and uid == 0:
        try:
          object.uid = self.newUid()
        except ConflictError:
          raise
        except:
          raise RuntimeError, 'could not set missing uid for %r' % (object,)
      elif check_uid:
        if uid in assigned_uid_dict:
            error_message = 'uid of %r is %r and ' \
                  'is already assigned to %s in catalog !!! This can be fatal.' % \
                  (object, uid, assigned_uid_dict[uid])
            if not self.sql_catalog_raise_error_on_uid_check:
                LOG("SQLCatalog.catalogObjectList", ERROR, error_message)
            else:
                raise ValueError(error_message)

        path = object.getPath()
        index = path_uid_dict.get(path)
        if index is not None:
          if index < 0:
            raise CatalogError, 'A negative uid %d is used for %s. Your catalog is broken. Recreate your catalog.' % (index, path)
          if uid != index or isinstance(uid, int):
            # We want to make sure that uid becomes long if it is an int
            error_message = 'uid of %r changed from %r (property) to %r '\
	                    '(catalog, by path) !!! This can be fatal' % (object, uid, index)
            if not self.sql_catalog_raise_error_on_uid_check:
              LOG("SQLCatalog.catalogObjectList", ERROR, error_message)
            else:
              raise ValueError(error_message)
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
            lock = self.__class__._reserved_uid_lock
            try:
              lock.acquire()
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
              lock.release()
          elif catalog_path == 'deleted':
            # Two possible cases:
            # - Reindexed object's path changed (ie, it or at least one of its
            #   parents was renamed) but unindexObject was not called yet.
            #   Reindexing is harmelss: unindexObject and then an
            #   immediateReindexObject will be called.
            # - Reindexed object was deleted by a concurrent transaction, which
            #   committed after we got our ZODB snapshot of this object.
            #   Reindexing is harmless: unindexObject will be called, and
            #   cannot be executed in parallel thanks to activity's
            #   serialisation_tag (so we cannot end up with a fantom object in
            #   catalog).
            # So we index object.
            # We could also not index it to save the time needed to index, but
            # this would slow down all regular case to slightly improve an
            # exceptional case.
            pass
          elif catalog_path is not None:
            # An uid conflict happened... Why?
            # can be due to path length
            if len(path) > MAX_PATH_LEN:
              LOG('SQLCatalog', ERROR, 'path of object %r is too long for catalog. You should use a shorter path.' %(object,))

            LOG('SQLCatalog', ERROR,
                'uid of %r changed from %r to %r as old one is assigned'
                ' to %s in catalog !!! This can be fatal.' % (
                object, uid, object.uid, catalog_path))

            error_message = 'uid of %r is %r and ' \
                            'is already assigned to %s in catalog !!! This can be fatal.' \
                            % (object, uid, catalog_path)
            if not self.sql_catalog_raise_error_on_uid_check:
                LOG('SQLCatalog', ERROR, error_message)
            else:
                raise ValueError(error_message)
            uid = object.uid

        assigned_uid_dict[uid] = object

    if method_id_list is None:
      method_id_list = self.sql_catalog_object_list
    econtext = getEngine().getContext()
    if disable_cache:
      argument_cache = DummyDict()
    else:
      argument_cache = {}

    with (noReadOnlyTransactionCache if disable_cache else
          readOnlyTransactionCache)():
      filter_dict = self.filter_dict
      catalogged_object_list_cache = {}
      for method_name in method_id_list:
        # We will check if there is an filter on this
        # method, if so we may not call this zsqlMethod
        # for this object
        expression = None
        try:
          filter = filter_dict[method_name]
          if filter['filtered']:
            if filter.get('type'):
              expression = Expression('python: context.getPortalType() in '
                                      + repr(tuple(filter['type'])))
              LOG('SQLCatalog', WARNING,
                  "Convert deprecated type filter for %r into %r expression"
                  % (method_name, expression.text))
              filter['type'] = ()
              filter['expression'] = expression.text
              filter['expression_instance'] = expression
            else:
              expression = filter['expression_instance']
        except KeyError:
          pass
        if expression is None:
          catalogged_object_list = object_list
        else:
          text = expression.text
          catalogged_object_list = catalogged_object_list_cache.get(text)
          if catalogged_object_list is None:
            catalogged_object_list_cache[text] = catalogged_object_list = []
            append = catalogged_object_list.append
            old_context = new_context_search(text) is None
            if old_context:
              warnings.warn("Filter expression for %r (%r): using variables"
                            " other than 'context' is deprecated and slower."
                            % (method_name, text), DeprecationWarning)
            expression_cache_key_list = filter.get('expression_cache_key', ())
            expression_result_cache = {}
            for object in object_list:
              if expression_cache_key_list:
                # Expressions are slow to evaluate because they are executed
                # in restricted environment. So we try to save results of
                # expressions by portal_type or any other key.
                # This cache is built each time we reindex
                # objects but we could also use over multiple transactions
                # if this can improve performance significantly
                # ZZZ - we could find a way to compute this once only
                cache_key = tuple(object.getProperty(key) for key
                                  in expression_cache_key_list)
                try:
                  if expression_result_cache[cache_key]:
                    append(object)
                  continue
                except KeyError:
                  pass
              if old_context:
                result = expression(self.getExpressionContext(object))
              else:
                econtext.setLocal('context', object)
                result = expression(econtext)
              if expression_cache_key_list:
                expression_result_cache[cache_key] = result
              if result:
                append(object)

        if not catalogged_object_list:
          continue

        #LOG('catalogObjectList', 0, 'method_name = %s' % (method_name,))
        method = getattr(self, method_name)
        if method.meta_type in ("Z SQL Method", "LDIF Method"):
          # Build the dictionnary of values
          arguments = method.arguments_src.split()
        elif method.meta_type == "Script (Python)":
          arguments = \
            method.func_code.co_varnames[:method.func_code.co_argcount]
        else:
          arguments = []
        kw = {x: LazyIndexationParameterList(catalogged_object_list,
                                             x, argument_cache)
          for x in arguments}

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

  def getCatalogMethodIds(self,
      valid_method_meta_type_list=valid_method_meta_type_list):
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

  def getPythonMethodIds(self):
    """
      Returns a list of all python scripts available in
      current sql catalog.
    """
    return self.getCatalogMethodIds(valid_method_meta_type_list=('Script (Python)', ))

  @transactional_cache_decorator('SQLCatalog._getSQLCatalogRelatedKeyList')
  def _getSQLCatalogRelatedKeySet(self):
    column_map = self.getColumnMap()
    column_set = set(column_map)
    for related_key in self.sql_catalog_related_keys:
      split_entire_definition = related_key.split('|')
      if len(split_entire_definition) != 2:
        LOG('SQLCatalog', WARNING, 'Malformed related key definition: %r. Ignored.' % (related_key, ))
        continue
      related_key_id = split_entire_definition[0].strip()
      if related_key_id in column_set and \
         related_key_id not in related_key_warned_column_set:
        related_key_warned_column_set.add(related_key_id)
        if related_key_id in column_map:
          LOG('SQLCatalog', WARNING, 'Related key %r has the same name as an existing column on tables %r' % (related_key_id, column_map[related_key_id]))
        else:
          LOG('SQLCatalog', WARNING, 'Related key %r is declared more than once.' % (related_key_id, ))
      column_set.add(related_key_id)
    return column_set

  def getSQLCatalogRelatedKeyList(self, key_list=None):
    """
    Return the list of related keys.
    This method can be overidden in order to implement
    dynamic generation of some related keys.
    """
    if key_list is None:
      key_list = []
    column_map = self._getSQLCatalogRelatedKeySet()
    return self.getDynamicRelatedKeyList(
      [k for k in key_list if k not in column_map],
      sql_catalog_id=self.id,
    ) + list(self.sql_catalog_related_keys)

  # Compatibililty SQL Sql
  getSqlCatalogRelatedKeyList = getSQLCatalogRelatedKeyList

  def getSQLCatalogScriptableKeyList(self):
    """
    Return the list of scriptable keys.
    """
    return self.sql_catalog_scriptable_keys

  @transactional_cache_decorator('SQLCatalog.getTableIndex')
  def _getTableIndex(self, table):
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
    return table_index

  def getTableIndex(self, table):
    """
    Return a map between index and column for a given table
    """
    return self._getTableIndex(table).copy()

  def isValidColumn(self, column_id):
    """
      Tells wether given name is or not an existing column.

      Warning: This includes "virtual" columns, such as related keys and
      scriptable keys.
    """
    result = self.getScriptableKeyScript(column_id) is not None
    if not result:
      result = column_id in self.getColumnMap()
      if not result:
        result = self.getRelatedKeyDefinition(column_id) is not None
    return result

  def getRelatedKeyDefinition(self, key):
    """
      Returns the definition of given related key name if found, None
      otherwise.
    """
    related_key_definition_cache = getTransactionalVariable().setdefault(
      'SQLCatalog.getRelatedKeyDefinition', {})
    try:
      result = related_key_definition_cache[key]
    except KeyError:
      for entire_definition in self.getSQLCatalogRelatedKeyList([key]):
        split_entire_definition = entire_definition.split('|')
        if len(split_entire_definition) != 2:
          LOG('SQLCatalog', WARNING, 'Malformed related key definition: %r. Ignored.' % (entire_definition, ))
          continue
        if split_entire_definition[0].strip() == key:
          result = split_entire_definition[1].strip()
          break
      else:
        result = None
      related_key_definition_cache[key] = result
    return result

  @transactional_cache_decorator('SQLCatalog._getgetScriptableKeyDict')
  def _getgetScriptableKeyDict(self):
    result = {}
    for scriptable_key_definition in self.sql_catalog_scriptable_keys:
      split_scriptable_key_definition = scriptable_key_definition.split('|')
      if len(split_scriptable_key_definition) != 2:
        LOG('SQLCatalog', WARNING, 'Malformed scriptable key definition: %r. Ignored.' % (scriptable_key_definition, ))
        continue
      key, script_id = [x.strip() for x in split_scriptable_key_definition]
      script = getattr(self, script_id, None)
      if script is None:
        LOG('SQLCatalog', WARNING, 'Scriptable key %r script %r is missing.' \
            ' Skipped.' % (key, script_id))
      else:
        result[key] = script
    return result

  def getScriptableKeyScript(self, key):
    return self._getgetScriptableKeyDict().get(key)

  def getColumnSearchKey(self, key, search_key_name=None):
    """
      Return a SearchKey instance for given key, using search_key_name
      as a SearchKey name if given, otherwise guessing from catalog
      configuration. If there is no search_key_name given and no
      SearchKey can be found, return None.

      Also return a related key definition string with following rules:
       - If returned SearchKey is a RelatedKey, value is its definition
       - Otherwise, value is None

      If both a related key and a real column are found, the related key
      is used.
    """
    # Is key a related key or a "real" column ?
    related_key_definition = self.getRelatedKeyDefinition(key)
    if related_key_definition is None:
      if key in self.getColumnMap():
        search_key = self.getSearchKey(key, search_key_name)
      else:
        search_key = None
    else:
      search_key = self.getSearchKey(key, 'RelatedKey')
    return search_key, related_key_definition

  def hasColumn(self, column):
    return self.getColumnSearchKey(column)[0] is not None

  def getColumnDefaultSearchKey(self, key, search_key_name=None):
    """
      Return a SearchKey instance which would ultimately receive the value
      associated with given key.
    """
    search_key, related_key_definition = self.getColumnSearchKey(key,
      search_key_name=search_key_name)
    if search_key is None:
      result = None
    else:
      if related_key_definition is not None:
        search_key = search_key.getSearchKey(sql_catalog=self,
          related_key_definition=related_key_definition)
    return search_key

  def buildSingleQuery(self, key, value, search_key_name=None, logical_operator=None, comparison_operator=None):
    """
      From key and value, determine the SearchKey to use and generate a Query
      from it.
    """
    script = self.getScriptableKeyScript(key)
    if script is None:
      search_key, related_key_definition = self.getColumnSearchKey(key, search_key_name)
      if search_key is None:
        result = None
      else:
        if related_key_definition is None:
          build_key = search_key
        else:
          build_key = search_key.getSearchKey(sql_catalog=self,
            related_key_definition=related_key_definition,
            search_key_name=search_key_name)
        result = build_key.buildQuery(value, logical_operator=logical_operator,
                                      comparison_operator=comparison_operator)
        if related_key_definition is not None:
          result = search_key.buildQuery(sql_catalog=self,
            related_key_definition=related_key_definition,
            search_value=result)
    else:
      result = script(value)
    return result

  def _buildQueryFromAbstractSyntaxTreeNode(self, node, search_key, wrap):
    if search_key.dequoteParsedText():
      _dequote = dequote
    else:
      _dequote = lambda x: x
    if node.isLeaf():
      result = search_key.buildQuery(wrap(_dequote(node.getValue())),
        comparison_operator=node.getComparisonOperator())
    elif node.isColumn():
      result = self.buildQueryFromAbstractSyntaxTreeNode(node.getSubNode(), node.getColumnName())
    else:
      query_list = []
      value_dict = {}
      append = query_list.append
      for subnode in node.getNodeList():
        if subnode.isLeaf():
          value_dict.setdefault(subnode.getComparisonOperator(),
            []).append(wrap(_dequote(subnode.getValue())))
        else:
          subquery = self._buildQueryFromAbstractSyntaxTreeNode(subnode, search_key, wrap)
          if subquery is not None:
            append(subquery)
      logical_operator = node.getLogicalOperator()
      if logical_operator == 'not':
        query_logical_operator = None
      else:
        query_logical_operator = logical_operator
      for comparison_operator, value_list in value_dict.iteritems():
        append(search_key.buildQuery(value_list, comparison_operator=comparison_operator, logical_operator=query_logical_operator))
      if logical_operator == 'not' or len(query_list) > 1:
        result = ComplexQuery(query_list, logical_operator=logical_operator)
      elif len(query_list) == 1:
        result = query_list[0]
      else:
        result = None
    return result

  def buildQueryFromAbstractSyntaxTreeNode(self, node, key, wrap=lambda x: x):
    """
      Build a query from given Abstract Syntax Tree (AST) node by recursing in
      its childs.
      This method calls itself recursively when walking the tree.

      node
        AST node being treated.
      key
        Default column (used when there is no explicit column in an AST leaf).

      Expected node API is described in interfaces/abstract_syntax_node.py .
    """
    script = self.getScriptableKeyScript(key)
    if script is None:
      search_key, related_key_definition = self.getColumnSearchKey(key)
    else:
      search_key = SearchKeyWrapperForScriptableKey(key, script)
      related_key_definition = None
    if search_key is None:
      # Unknown, skip loudly
      LOG('SQLCatalog', WARNING, 'Unknown column %r, skipped.' % (key, ))
      result = None
    else:
      if related_key_definition is None:
        build_key = search_key
      else:
        build_key = search_key.getSearchKey(sql_catalog=self,
          related_key_definition=related_key_definition)
      result = self._buildQueryFromAbstractSyntaxTreeNode(node, build_key,
        wrap)
      if related_key_definition is not None:
        result = search_key.buildQuery(sql_catalog=self,
          related_key_definition=related_key_definition,
          search_value=result)
    return result

  def _parseSearchText(self, search_key, search_text, is_valid=None):
    if is_valid is None:
      is_valid = self.isValidColumn
    return search_key.parseSearchText(search_text, is_valid)

  def parseSearchText(self, search_text, column=None, search_key=None,
                      is_valid=None):
    if column is None and search_key is None:
      raise ValueError, 'One of column and search_key must be different '\
                        'from None'
    return self._parseSearchText(self.getSearchKey(
      column, search_key=search_key), search_text, is_valid=is_valid)

  def buildQuery(self, kw, ignore_empty_string=True, operator='and'):
    query_list = []
    append = query_list.append
    # unknown_column_dict: contains all (key, value) pairs which could not be
    # changed into queries. This is here for backward compatibility, because
    # scripts can invoke this method and expect extra parameters (such as
    # from_expression) to be handled. As they are normaly handled at
    # buildSQLQuery level, we must store them into final ComplexQuery, which
    # will handle them.
    unknown_column_dict = {}
    # empty_value_dict: contains all keys whose value causes them to be
    # discarded.
    empty_value_dict = {}
    for key, value in kw.iteritems():
      result = None
      if isinstance(value, dict_type_list):
        # Cast dict-ish types into plain dicts.
        value = dict(value)
      if ignore_empty_string and (
          value == ''
          or (isinstance(value, list_type_list) and not value)
          or (isinstance(value, dict) and (
            'query' not in value
            or value['query'] == ''
            or (isinstance(value['query'], list_type_list)
              and not value['query'])))):
        # We have an empty value, do not create a query from it
        empty_value_dict[key] = value
      else:
        script = self.getScriptableKeyScript(key)
        if isinstance(value, dict):
          # Dictionnary: might contain the search key to use.
          search_key_name = value.get('key')
          # Backward compatibility: former "Keyword" key is now named
          # "KeywordKey".
          if search_key_name == 'Keyword':
            search_key_name = value['key'] = 'KeywordKey'
          # Backward compatibility: former "ExactMatch" is now only available
          # as "RawKey"
          elif search_key_name == 'ExactMatch':
            search_key_name = value['key'] = 'RawKey'
        if isinstance(value, _Query):
          # Query instance: use as such, ignore key.
          result = value
        elif script is not None:
          result = script(value)
        elif isinstance(value, (basestring, dict)):
          # String: parse using key's default search key.
          raw_value = value
          if isinstance(value, dict):
            # De-wrap value for parsing, and re-wrap when building queries.
            def wrap(x):
              result = raw_value.copy()
              result['query'] = x
              return result
            value = value['query']
          else:
            wrap = lambda x: x
            search_key_name = None
          search_key = self.getColumnDefaultSearchKey(key,
            search_key_name=search_key_name)
          if search_key is not None:
            if isinstance(value, basestring):
              abstract_syntax_tree = self._parseSearchText(search_key, value)
            else:
              abstract_syntax_tree = None
            if abstract_syntax_tree is None:
              # Parsing failed, create a query from the bare string.
              result = self.buildSingleQuery(key, raw_value, search_key_name)
            else:
              result = self.buildQueryFromAbstractSyntaxTreeNode(
                abstract_syntax_tree, key, wrap)
        else:
          # Any other type, just create a query. (can be a DateTime, ...)
          result = self.buildSingleQuery(key, value)
        if result is None:
          # No query could be created, emit a log, add to unknown column dict.
          unknown_column_dict[key] = value
        else:
          append(result)
    if len(empty_value_dict):
      LOG('SQLCatalog', WARNING, 'Discarding columns with empty values: %r' % (empty_value_dict, ))
    if len(unknown_column_dict):
      LOG('SQLCatalog', WARNING, 'Unknown columns %r, skipped.' % (unknown_column_dict.keys(), ))
    return ComplexQuery(query_list, logical_operator=operator,
        unknown_column_dict=unknown_column_dict)

  def buildOrderByList(self, sort_on=None, sort_order=None, order_by_expression=None):
    """
      Internal method. Should not be used by code outside buildSQLQuery.

      It is in a separate method because this code is here to keep backward
      compatibility with an ambiguous API, and as such is ugly. So it's better
      to conceal it to its own method.

      It does not preserve backward compatibility for:
        'sort-on' parameter
        'sort-on' property
        'sort-order' parameter
        'sort-order' property
    """
    order_by_list = []
    append = order_by_list.append
    if sort_on is not None:
      if order_by_expression is not None:
        LOG('SQLCatalog', WARNING, 'order_by_expression (%r) and sort_on (%r) were given. Ignoring order_by_expression.' % (order_by_expression, sort_on))
      if not isinstance(sort_on, (tuple, list)):
        sort_on = [[sort_on]]
      for item in sort_on:
        if isinstance(item, (tuple, list)):
          item = list(item)
        else:
          item = [item]
        if sort_order is not None and len(item) == 1:
          item.append(sort_order)
        if len(item) > 1:
          if item[1] in ('descending', 'reverse', 'DESC'):
            item[1] = 'DESC'
          else:
            item[1] = 'ASC'
          if len(item) > 2:
            if item[2] == 'int':
              item[2] = 'SIGNED'
        append(item)
    elif order_by_expression is not None:
      if not isinstance(order_by_expression, basestring):
        raise TypeError, 'order_by_expression must be a basestring instance. Got %r.' % (order_by_expression, )
      order_by_list = [[x.strip()] for x in order_by_expression.split(',')]
    return order_by_list

  def buildEntireQuery(self, kw, query_table='catalog', ignore_empty_string=1,
                       limit=None, extra_column_list=()):
    group_by_list = kw.pop('group_by_list', kw.pop('group_by', kw.pop('group_by_expression', ())))
    if isinstance(group_by_list, basestring):
      group_by_list = [x.strip() for x in group_by_list.split(',')]
    select_dict = kw.pop('select_dict', kw.pop('select_list', kw.pop('select_expression', None)))
    if isinstance(select_dict, basestring):
      if len(select_dict):
        real_select_dict = {}
        for column in select_dict.split(','):
          index = column.lower().find(' as ')
          if index != -1:
            real_select_dict[column[index + 4:].strip()] = column[:index].strip()
          else:
            real_select_dict[column.strip()] = None
        select_dict = real_select_dict
      else:
        select_dict = None
    elif isinstance(select_dict, (list, tuple)):
      select_dict = dict.fromkeys(select_dict)
    # Handle left_join_list
    left_join_list = kw.pop('left_join_list', ())
    # Handle implicit_join. It's True by default, as there's a lot of code
    # in BT5s and elsewhere that calls buildSQLQuery() expecting implicit
    # join. self._queryResults() defaults it to False for those using
    # catalog.searchResults(...) or catalog(...) directly.
    implicit_join = kw.pop('implicit_join', True)
    # Handle order_by_list
    order_by_list = kw.pop('order_by_list', None)
    sort_on = kw.pop('sort_on', None)
    sort_order = kw.pop('sort_order', None)
    order_by_expression = kw.pop('order_by_expression', None)
    if order_by_list is None:
      order_by_list = self.buildOrderByList(
        sort_on=sort_on,
        sort_order=sort_order,
        order_by_expression=order_by_expression
      )
    else:
      if sort_on is not None:
        LOG('SQLCatalog', WARNING, 'order_by_list and sort_on were given, ignoring sort_on.')
      if sort_order is not None:
        LOG('SQLCatalog', WARNING, 'order_by_list and sort_order were given, ignoring sort_order.')
      if order_by_expression is not None:
        LOG('SQLCatalog', WARNING, 'order_by_list and order_by_expression were given, ignoring order_by_expression.')
    # Handle from_expression
    from_expression = kw.pop('from_expression', None)
    # Handle where_expression
    where_expression = kw.get('where_expression', None)
    if isinstance(where_expression, basestring) and len(where_expression):
      LOG('SQLCatalog', INFO, 'Giving where_expression a string value is deprecated.')
      # Transform given where_expression into a query, and update kw.
      kw['where_expression'] = SQLQuery(where_expression)
    # Handle select_expression_key
    # It is required to support select_expression_key parameter for backward
    # compatiblity, but I'm not sure if there can be a serious use for it in
    # new API.
    order_by_override_list = kw.pop('select_expression_key', ())
    return EntireQuery(
      query=self.buildQuery(kw, ignore_empty_string=ignore_empty_string),
      order_by_list=order_by_list,
      order_by_override_list=order_by_override_list,
      group_by_list=group_by_list,
      select_dict=select_dict,
      left_join_list=left_join_list,
      implicit_join=implicit_join,
      limit=limit,
      catalog_table_name=query_table,
      extra_column_list=extra_column_list,
      from_expression=from_expression)

  def buildSQLQuery(self, query_table='catalog', REQUEST=None,
                          ignore_empty_string=1, only_group_columns=False,
                          limit=None, extra_column_list=(),
                          **kw):
    query = self.buildEntireQuery(kw, query_table=query_table,
      ignore_empty_string=ignore_empty_string, limit=limit,
      extra_column_list=extra_column_list)
    result = query.asSQLExpression(self, only_group_columns).asSQLExpressionDict()
    return result

  # Compatibililty SQL Sql
  buildSqlQuery = buildSQLQuery

  @transactional_cache_decorator('SQLCatalog._getSearchKeyDict')
  def _getSearchKeyDict(self):
    result = {}
    search_key_column_dict = {
      'KeywordKey': self.sql_catalog_keyword_search_keys,
      'FullTextKey': self.sql_catalog_full_text_search_keys,
      'DateTimeKey': self.sql_catalog_datetime_search_keys,
    }
    for key, column_list in search_key_column_dict.iteritems():
      for column in column_list:
        if column in result:
          LOG('SQLCatalog', WARNING, 'Ambiguous configuration: column %r is set to use %r key, but also to use %r key. Former takes precedence.' % (column, result[column], key))
        else:
          result[column] = key
    for line in self.sql_catalog_search_keys:
      try:
        column, key = [x.strip() for x in line.split('|', 2)]
        result[column] = key
      except ValueError:
        LOG('SQLCatalog', WARNING, 'Wrong configuration for sql_catalog_search_keys: %r' % line)
    return result

  def getSearchKey(self, column, search_key=None):
    """
      Return an instance of a SearchKey class.

      column (string)
        The column for which the search key will be returned.
      search_key (string)
        If given, must be the name of a SearchKey class to be returned.
        Returned value will be an instance of that class, even if column has
        been configured to use a different one.
    """
    if search_key is None:
      search_key = self._getSearchKeyDict().get(column, 'DefaultKey')
    return getSearchKeyInstance(search_key, column)

  def getComparisonOperator(self, operator):
    """
      Return an instance of an Operator class.

      operator (string)
        String defining the expected operator class.
        See Operator module to have a list of available operators.
    """
    return getComparisonOperatorInstance(operator)

  PROPAGATE_PARAMETER_SET = ('selection_domain',
                             'selection_report',
                             # XXX should get the next parameters from
                             # the ZSQLMethod class itself
                             'zsql_brain')
  def _queryResults(self, REQUEST=None, build_sql_query_method=None, **kw):
    """ Returns a list of brains from a set of constraints on variables """
    if build_sql_query_method is None:
      build_sql_query_method = self.buildSQLQuery
    kw.setdefault('implicit_join', False)
    query = build_sql_query_method(REQUEST=REQUEST, **kw)
    # XXX: decide if this should be made normal
    ENFORCE_SEPARATION = True
    if ENFORCE_SEPARATION:
      # Some parameters must be propagated:
      kw = {name: kw[name] for name in self.PROPAGATE_PARAMETER_SET
                           if name in kw}
    kw['where_expression'] = query['where_expression']
    kw['sort_on'] = query['order_by_expression']
    kw['from_table_list'] = query['from_table_list']
    kw['from_expression'] = query['from_expression']
    kw['limit_expression'] = query['limit_expression']
    kw['select_expression'] = query['select_expression']
    kw['group_by_expression'] = query['group_by_expression']
    # XXX: why not kw.update(query)??
    return kw

  def queryResults(self, sql_method, REQUEST=None, src__=0, build_sql_query_method=None, **kw):
    sql_kw = self._queryResults(REQUEST=REQUEST, build_sql_query_method=build_sql_query_method, **kw)
    return sql_method(src__=src__, **sql_kw)

  def getSearchResultsMethod(self):
    return getattr(self, self.sql_search_results)

  def searchResults(self, REQUEST=None, **kw):
    """ Returns a list of brains from a set of constraints on variables """
    if 'only_group_columns' in kw:
      # searchResults must be consistent in API with countResults
      raise ValueError('only_group_columns does not belong to this API '
        'level, use queryResults directly')
    return self.queryResults(
      self.getSearchResultsMethod(),
      REQUEST=REQUEST,
      extra_column_list=self.getCatalogSearchResultKeys(),
      **kw
    )

  __call__ = searchResults

  def getCountResultsMethod(self):
    return getattr(self, self.sql_count_results)

  def countResults(self, REQUEST=None, **kw):
    """ Returns the number of items which satisfy the where_expression """
    return self.queryResults(
      self.getCountResultsMethod(),
      REQUEST=REQUEST,
      extra_column_list=self.getCatalogSearchResultKeys(),
      only_group_columns=True,
      **kw
    )

  def isAdvancedSearchText(self, search_text):
    return isAdvancedSearchText(search_text, self.isValidColumn)

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

        if REQUEST.has_key('%s_box' % id):
          self.filter_dict[id]['filtered'] = 1
        else:
          self.filter_dict[id]['filtered'] = 0

        expression = REQUEST.get('%s_expression' % id, '').strip()
        self.filter_dict[id]['expression'] = expression
        if expression:
          self.filter_dict[id]['expression_instance'] = Expression(expression)
        else:
          self.filter_dict[id]['expression_instance'] = None

        if REQUEST.has_key('%s_type' % id):
          list_type = REQUEST['%s_type' % id]
          if isinstance(list_type, str):
            list_type = [list_type]
          self.filter_dict[id]['type'] = list_type
        else:
          self.filter_dict[id]['type'] = []

        self.filter_dict[id]['expression_cache_key'] = \
          tuple(sorted(REQUEST.get('%s_expression_cache_key' % id, '').split()))

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
        return ' '.join(self.filter_dict[method_name]['expression_cache_key'])
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

  def setFilterExpression(self, method_name, expression):
    """ Set the Expression for a certain method name. This allow set
        expressions by scripts.
    """
    if withCMF:
      if getattr(aq_base(self), 'filter_dict', None) is None:
        self.filter_dict = PersistentMapping()
        return None
      self.filter_dict[method_name]['expression'] = expression
      if expression:
        self.filter_dict[method_name]['expression_instance'] = Expression(expression)
      else:
        self.filter_dict[method_name]['expression_instance'] = None

  def isPortalTypeSelected(self, method_name, portal_type):
    """ Returns true if the portal type is selected for this method.
      XXX deprecated
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
      XXX deprecated
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

  def getFilterDict(self):
    """
      Utility Method.
      Filter Dict is a dictionary and used at Python Scripts,
      This method returns a filter dict as a dictionary.
    """
    if withCMF:
      if getattr(aq_base(self), 'filter_dict', None) is None:
        self.filter_dict = PersistentMapping()
        return None
      filter_dict = {}
      for key in self.filter_dict:
        # Filter is also a Persistence dict.
        filter_dict[key] = {}
        for sub_key in self.filter_dict[key]:
           filter_dict[key][sub_key] = self.filter_dict[key][sub_key]
      return filter_dict
    return None

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
      XXX deprecated
      '''
      if withCMF:
        data = {
            'here':         ob,
            'container':    aq_parent(aq_inner(ob)),
            #'root':         ob.getPhysicalRoot(),
            #'request':      getattr( ob, 'REQUEST', None ),
            #'modules':      SecureModuleImporter,
            #'user':         getSecurityManager().getUser(),
            # XXX these below are defined, because there is no
            # accessor for some attributes, and restricted environment
            # may not access them directly.
            'isDelivery':   ob.isDelivery,
            'isMovement':   ob.isMovement,
            'isPredicate':  ob.isPredicate,
            'isDocument':   ob.isDocument,
            'isInventory':  ob.isInventory,
            'isInventoryMovement': ob.isInventoryMovement,
            }
        return getEngine().getContext(data)


InitializeClass(Catalog)

class CatalogError(Exception): pass

from Query.Query import Query as _Query
from Query.SimpleQuery import SimpleQuery
from Query.ComplexQuery import ComplexQuery
from Query.AutoQuery import AutoQuery
Query = AutoQuery

def NegatedQuery(query):
  return ComplexQuery(query, logical_operator='not')

def AndQuery(*args):
  return ComplexQuery(logical_operator='and', *args)

def OrQuery(*args):
  return ComplexQuery(logical_operator='or', *args)

allow_class(SimpleQuery)
allow_class(ComplexQuery)

import SearchKey
SEARCH_KEY_INSTANCE_POOL = {}
SEARCH_KEY_CLASS_CACHE = {}

def getSearchKeyInstance(search_key_class_name, column):
  assert isinstance(search_key_class_name, basestring)
  try:
    search_key_class = SEARCH_KEY_CLASS_CACHE[search_key_class_name]
  except KeyError:
    search_key_class = getattr(getattr(SearchKey, search_key_class_name),
                               search_key_class_name)
    SEARCH_KEY_CLASS_CACHE[search_key_class_name] = search_key_class
  try:
    instance_dict = SEARCH_KEY_INSTANCE_POOL[search_key_class]
  except KeyError:
    instance_dict = SEARCH_KEY_INSTANCE_POOL[search_key_class] = {}
  try:
    result = instance_dict[column]
  except KeyError:
    result = instance_dict[column] = search_key_class(column)
  return result

class SearchKeyWrapperForScriptableKey(SearchKey.SearchKey.SearchKey):
  """
    This SearchKey is a simple wrapper around a ScriptableKey, so such script
    can be used in place of a regular SearchKey.
  """
  default_comparison_operator = None
  get_operator_from_value = False

  def __init__(self, column, script):
    self.script = script
    super(SearchKeyWrapperForScriptableKey, self).__init__(column)

  def buildQuery(self, search_value, group=None, logical_operator=None,
                 comparison_operator=None):
    # XXX: It would be better to extend ScriptableKey API to support other
    # parameters.
    if group is not None:
      raise ValueError, 'ScriptableKey cannot be used inside a group ' \
        '(%r given).' % (group, )
    if logical_operator is not None:
      raise ValueError, 'ScriptableKey ignores logical operators ' \
        '(%r given).' % (logical_operator, )
    if comparison_operator != '':
      raise ValueError, 'ScriptableKey ignores comparison operators ' \
        '(%r given).' % (comparison_operator, )
    return self.script(search_value)

from Operator import operator_dict
def getComparisonOperatorInstance(operator):
  return operator_dict[operator]

from Query.EntireQuery import EntireQuery
from Query.SQLQuery import SQLQuery

verifyClass(ISearchKeyCatalog, Catalog)
