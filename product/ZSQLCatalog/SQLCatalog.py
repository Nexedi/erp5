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
from AccessControl.Permissions import (
  access_contents_information,
  import_export_objects,
  manage_zcatalog_entries,
)
from AccessControl.SimpleObjectPolicies import ContainerAssertions
from BTrees.OIBTree import OIBTree
from App.config import getConfiguration
from BTrees.Length import Length
from Shared.DC.ZRDB.DA import DatabaseError
from Shared.DC.ZRDB.TM import TM

from Acquisition import aq_parent, aq_inner, aq_base
from zLOG import LOG, WARNING, INFO, TRACE, ERROR
from ZODB.POSException import ConflictError
from Products.CMFCore import permissions
from Products.PythonScripts.Utility import allow_class

from functools import wraps
import time
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

@contextmanager
def noReadOnlyTransactionCache():
  yield
try:
  from Products.ERP5Type.Cache import readOnlyTransactionCache
except ImportError:
  LOG('SQLCatalog', WARNING, 'Count not import readOnlyTransactionCache, expect slowness.')
  readOnlyTransactionCache = noReadOnlyTransactionCache

try:
  from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
except ImportError:
  LOG('SQLCatalog', WARNING, 'Count not import getTransactionalVariable, expect slowness.')
  def getTransactionalVariable():
    return {}
  def transactional_cache_decorator(method):
    return method
else:
  def transactional_cache_decorator(method):
    """
    Implements singleton-style caching.
    Wrapped method must have no parameters (besides "self").
    """
    cache_id = id(method)
    @wraps(method)
    def wrapper(self):
      # XXX: getPhysicalPath is overkill for a unique cache identifier.
      # What I would like to use instead of it is:
      #   (self._p_jar.db().database_name, self._p_oid)
      # but database_name is not unique in at least ZODB 3.4 (Zope 2.8.8).
      try:
        instance_id = self._v_physical_path
      except AttributeError:
        self._v_physical_path = instance_id = self.getPhysicalPath()
      try:
        return getTransactionalVariable()[(
          cache_id,
          self._cache_sequence_number,
          instance_id,
        )]
      except KeyError:
        getTransactionalVariable()[(
          cache_id,
          self._cache_sequence_number,
          instance_id,
        )] = result = method(self)
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
DOMAIN_STRICT_MEMBERSHIP_DICT = {
  'selection_domain': False,
  'selection_report': True,
}

manage_addSQLCatalogForm = DTMLFile('dtml/addSQLCatalog',globals())

# Here go uid buffers
# Structure:
#  global_uid_buffer_dict[catalog_path][thread_id] = UidBuffer
global_uid_buffer_dict = {}

# These are global variables on memory, so shared only by threads in the same Zope instance.
# This is used for exclusive access to the list of reserved uids.
global_reserved_uid_lock = allocate_lock()

# This is set to the time when reserved uids are cleared in this Zope instance.
global_clear_reserved_time = None

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
    try:
      value = self._global_cache[global_cache_key]
    except KeyError:
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
      self._global_cache[global_cache_key] = value
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
  (references in the metadata) that satisfy search conditions.

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
     ['manage_catalogView', 'manage_catalogFind',
      'manage_catalogFilter',
      'manage_catalogAdvanced',
      'manage_main',],
     ['Manager']),

    ('Search ZCatalog',
     ['searchResults', '__call__', 'uniqueValuesFor',
      'all_meta_types', 'valid_roles',
      'getCatalogSearchTableIds',
      'getFilterableMethodList',],
     ['Anonymous', 'Manager']),

    )

  _properties = (
    { 'id'      : 'title',
      'description' : 'The title of this catalog',
      'type'    : 'string',
      'mode'    : 'w' },

    # Z SQL Methods
    { 'id'      : 'sql_catalog_clear_reserved',
      'description' : 'A method to clear reserved uid values',
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
    { 'id'      : 'sql_optimizer_switch',
      'description': 'Method to get optimizer_switch value',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_schema',
      'description' : 'Method to get the main catalog schema',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_multi_schema',
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
      'description': 'Columns which should be used to map a monovalued local role',
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

  sql_catalog_delete_uid = ''
  sql_catalog_clear_reserved = ''
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
  sql_optimizer_switch = ''
  sql_search_tables = ()
  sql_catalog_schema = ''
  sql_catalog_multi_schema = ''
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

  # This is an instance id which specifies who owns which reserved uids.
  _instance_id = getattr(getConfiguration(), 'instance_id', None)

  manage_catalogView = DTMLFile('dtml/catalogView',globals())
  manage_catalogFilter = DTMLFile('dtml/catalogFilter',globals())
  manage_catalogFind = DTMLFile('dtml/catalogFind',globals())
  manage_catalogAdvanced = DTMLFile('dtml/catalogAdvanced', globals())

  _cache_sequence_number = 0
  HAS_ARGUMENT_SRC_METATYPE_SET = (
    "Z SQL Method",
    "LDIF Method",
  )
  HAS_FUNC_CODE_METATYPE_SET = (
    "Script (Python)",
  )

  def __init__(self, id, title='', container=None):
    if container is not None:
      self=self.__of__(container)
    self.id=id
    self.title=title
    self.schema = {}  # mapping from attribute name to column
    self.names = {}   # mapping from column to attribute name
    self.indexes = {}   # empty mapping
    self.filter_dict = PersistentMapping()

  def manage_afterClone(self, item):
    try:
      del self._v_physical_path
    except AttributeError:
      pass
    super(Catalog, self).manage_afterClone(item)

  security.declarePrivate('getCacheSequenceNumber')
  def getCacheSequenceNumber(self):
    return self._cache_sequence_number

  def _clearCaches(self):
    self._cache_sequence_number += 1

  def _getFilterDict(self):
    return self.filter_dict

  security.declarePrivate('getSQLCatalogRoleKeysList')
  def getSQLCatalogRoleKeysList(self):
    """
    Return the list of role keys.
    """
    role_key_dict = {}
    for role_key in self.sql_catalog_role_keys:
      role, column = role_key.split('|')
      role_key_dict[role.strip()] = column.strip()
    return role_key_dict.items()

  security.declareProtected(permissions.ManagePortal, 'getSQLCatalogSecurityUidGroupsColumnsDict')
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

  security.declarePrivate('getSQLCatalogLocalRoleKeysList')
  def getSQLCatalogLocalRoleKeysList(self):
    """
    Return the list of local role keys.
    """
    local_role_key_dict = {}
    for role_key in self.sql_catalog_local_role_keys:
      role, column = role_key.split('|')
      local_role_key_dict[role.strip()] = column.strip()
    return local_role_key_dict.items()

  security.declareProtected(manage_zcatalog_entries, 'manage_historyCompare')
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
      if key in self.security_uid_dict:
        local_roles_group_id_to_security_uid_mapping[local_roles_group_id] = self.security_uid_dict[key]
      elif allowed_roles_and_users in self.security_uid_dict and not local_roles_group_id:
        # This key is present in security_uid_dict without
        # local_roles_group_id, it has been inserted before
        # local_roles_group_id were introduced.
        local_roles_group_id_to_security_uid_mapping[local_roles_group_id] = self.security_uid_dict[allowed_roles_and_users]
      else:
        if not security_uid:
          getTransactionalVariable().pop('getSecurityUidDictAndRoleColumnDict',
                                         None)
          # We must keep compatibility with existing sites
          security_uid = getattr(self, 'security_uid_index', None)
          if security_uid is None:
            security_uid = 0
          # At some point, it was a Length
          elif isinstance(security_uid, Length):
            security_uid = security_uid()
        security_uid = int(
          self.getPortalObject().portal_ids.generateNewId(
            id_generator='uid',
            id_group='security_uid_index',
            default=security_uid,
          ),
        )

        self.security_uid_dict[key] = security_uid
        local_roles_group_id_to_security_uid_mapping[local_roles_group_id] = security_uid

        # If some optimised_roles_and_users are returned by this method it
        # means that new entries will have to be added to roles_and_users table.
        for user in allowed_roles_and_users:
          optimised_roles_and_users.append((security_uid, local_roles_group_id, user))

    return (local_roles_group_id_to_security_uid_mapping, optimised_roles_and_users)

  security.declarePrivate('getRoleAndSecurityUidList')
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

  def getSqlClearCatalogList(self):
    return self.sql_clear_catalog

  def _clear(self):
    """
    Clears the catalog by calling a list of methods
    """
    for method_name in self.getSqlClearCatalogList():
      method = self._getOb(method_name)
      try:
        method()
      except ConflictError:
        raise
      except:
        LOG('SQLCatalog', WARNING,
            'could not clear catalog with %s' % method_name, error=True)
        raise
    # Reserved uids have been removed.
    self._clearReserved()
    self._clearSecurityCache()
    self._clearSubjectCache()
    self._clearCaches()

  def _clearReserved(self):
    """
    Clears reserved uids
    """
    method_id = self.getSqlCatalogClearReserved()
    method = self._getOb(method_id)
    try:
      method()
    except ConflictError:
      raise
    except:
      LOG(
        'SQLCatalog',
        WARNING,
        'could not clear reserved catalog with %s' % method_id,
        error=True,
      )
      raise
    self._last_clear_reserved_time += 1

  def getSqlGetitemByUid(self):
    return self.sql_getitem_by_uid

  security.declarePrivate('getRecordForUid')
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
    search_result = self._getOb(self.getSqlGetitemByUid())(uid_list=[uid])
    if search_result:
      result, = search_result
      return result
    raise KeyError(uid)

  security.declarePrivate('editSchema')
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

  def getSqlSearchTablesList(self):
    return list(self.sql_search_tables)

  security.declarePrivate('getCatalogSearchTableIds')
  def getCatalogSearchTableIds(self):
    """Return selected tables of catalog which are used in JOIN.
       catalaog is always first
    """
    search_tables = self.getSqlSearchTablesList() or ['catalog']
    if search_tables[0] != 'catalog':
      search_tables = ['catalog'] + [x for x in search_tables if x != 'catalog']
      # XXX: cast to tuple to avoid a mutable persistent property ?
      self.sql_search_tables = search_tables
    return search_tables

  def getSqlSearchResultKeysList(self):
    return self.sql_search_result_keys

  security.declarePublic('getCatalogSearchResultKeys')
  def getCatalogSearchResultKeys(self):
    """Return search result keys.
    """
    return self.getSqlSearchResultKeysList()

  def getSqlCatalogMultiSchema(self):
    return self.sql_catalog_multi_schema

  def getSqlCatalogSchema(self):
    return self.sql_catalog_schema

  @transactional_cache_decorator
  def _getCatalogSchema(self):
    method = getattr(self, self.sql_catalog_multi_schema, None)
    result = {}
    if method is None:
      # BBB: deprecated
      warnings.warn("The usage of sql_catalog_schema is much slower. "
              "than sql_catalog_multi_schema. It makes many SQL queries "
              "instead of one",
              DeprecationWarning)
      method_name = self.getSqlCatalogSchema()
      try:
        method = getattr(self, method_name)
      except AttributeError:
        return {}
      for table in self.getCatalogSearchTableIds():
        try:
          result[table] = [c.Field for c in method(table=table)]
        except (ConflictError, DatabaseError):
          raise
        except Exception:
          LOG(
            'SQLCatalog',
            WARNING,
            '_getCatalogSchema failed with the method %s' % method_name,
            error=True,
          )
      return result
    for row in method():
      result.setdefault(row.TABLE_NAME, []).append(row.COLUMN_NAME)
    return result

  security.declarePrivate('getTableColumnList')
  def getTableColumnList(self, table):
    """
    Returns the list of columns in given table.
    Raises KeyError on unknown table.
    """
    return self._getCatalogSchema()[table]

  security.declarePublic('getColumnIds')
  @transactional_cache_decorator
  def getColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids
    """
    keys = set()
    add_key = keys.add
    table_dict = self._getCatalogSchema()
    for table in self.getCatalogSearchTableIds():
      for field in table_dict.get(table, ()):
        add_key(field)
        add_key('%s.%s' % (table, field))  # Is this inconsistent ?
    for related in self.getSQLCatalogRelatedKeyList():
      related_tuple = related.split('|')
      add_key(related_tuple[0].strip())
    for scriptable in self.getSQLCatalogScriptableKeyList():
      scriptable_tuple = scriptable.split('|')
      add_key(scriptable_tuple[0].strip())
    return sorted(keys)

  security.declarePrivate('getColumnMap')
  @transactional_cache_decorator
  def getColumnMap(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids
    """
    result = {}
    table_dict = self._getCatalogSchema()
    for table in self.getCatalogSearchTableIds():
      for field in table_dict.get(table, ()):
        result.setdefault(field, []).append(table)
        result.setdefault('%s.%s' % (table, field), []).append(table) # Is this inconsistent ?
    return result

  security.declarePublic('getResultColumnIds')
  @transactional_cache_decorator
  def getResultColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids
    """
    keys = set()
    table_dict = self._getCatalogSchema()
    for table in self.getCatalogSearchTableIds():
      for field in table_dict.get(table, ()):
        keys.add('%s.%s' % (table, field))
    return sorted(keys)

  security.declarePublic('getSortColumnIds')
  @transactional_cache_decorator
  def getSortColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids that can be used for a sort
    """
    keys = set()
    table_dict = self._getCatalogSchema()
    for table in self.getTableIds():
      for field in table_dict[table]:
        keys.add('%s.%s' % (table, field))
    return sorted(keys)

  security.declarePublic('getTableIds')
  def getTableIds(self):
    """
    Calls the show table method and returns dictionnary of
    Field Ids
    """
    return self._getCatalogSchema().keys()

  security.declarePrivate('getUIDBuffer')
  def getUIDBuffer(self, force_new_buffer=False):
    assert global_reserved_uid_lock.locked()
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
  security.declarePrivate('isIndexable')
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

  security.declarePrivate('getSiteRoot')
  def getSiteRoot(self):
    """
    Returns the root of the site
    """
    if withCMF:
      site_root = getToolByName(self, 'portal_url').getPortalObject()
    else:
      site_root = self.aq_parent
    return site_root

  security.declarePrivate('getZopeRoot')
  def getZopeRoot(self):
    """
    Returns the root of the zope
    """
    if withCMF:
      zope_root = getToolByName(self, 'portal_url').getPortalObject().aq_parent
    else:
      zope_root = self.getPhysicalRoot()
    return zope_root

  security.declarePrivate('newUid')
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
    global global_clear_reserved_time

    if not self.getPortalObject().isIndexable():
      return None

    with global_reserved_uid_lock:
      uid_buffer = self.getUIDBuffer(
        force_new_buffer=global_clear_reserved_time != self._last_clear_reserved_time,
      )
      global_clear_reserved_time = self._last_clear_reserved_time
      try:
        return long(uid_buffer.pop())
      except IndexError:
        uid_buffer.extend(
          self.getPortalObject().portal_ids.generateNewIdList(
            id_generator='uid',
            id_group='catalog_uid',
            id_count=UID_BUFFER_SIZE,
            default=getattr(self, '_max_uid', lambda: 1)(),
          ),
        )
        try:
          return long(uid_buffer.pop())
        except IndexError:
          raise CatalogError("Could not retrieve new uid")

  security.declareProtected(manage_zcatalog_entries, 'manage_catalogObject')
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

  security.declareProtected(manage_zcatalog_entries, 'manage_uncatalogObject')
  def manage_uncatalogObject(self, REQUEST, RESPONSE, URL1, urls=None):
    """ removes Zope object(s) 'urls' from catalog """

    if urls:
      if isinstance(urls, str):
        urls=(urls,)

      for url in urls:
        self.aq_parent.uncatalog_object(url, sql_catalog_id=self.id)

    RESPONSE.redirect(URL1 + '/manage_catalogView?manage_tabs_message=Object%20Uncataloged')

  security.declareProtected(manage_zcatalog_entries, 'manage_catalogClear')
  def manage_catalogClear(self, REQUEST=None, RESPONSE=None,
                          URL1=None, sql_catalog_id=None):
    """ clears the whole enchilada """
    self.beforeCatalogClear()

    self._clear()

    if RESPONSE and URL1:
      RESPONSE.redirect(
        '%s/manage_catalogAdvanced?manage_tabs_message=Catalog%%20Cleared' % URL1,
      )


  security.declareProtected(manage_zcatalog_entries, 'manage_catalogFoundItems')
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

  security.declarePrivate('catalogObject')
  def catalogObject(self, object, path, is_object_moved=0):
    """Add an object to the Catalog by calling all SQL methods and
    providing needed arguments.

    'object' is the object to be catalogged."""
    self._catalogObjectList([object])

  security.declarePrivate('catalogObjectList')
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

  def getSqlCatalogObjectListList(self):
    return self.sql_catalog_object_list

  def _catalogObjectList(self, object_list, method_id_list=None,
                         disable_cache=0, check_uid=1, idxs=None):
    """This is the real method to catalog objects."""
    if idxs not in (None, []):
      LOG('ZSLQCatalog.SQLCatalog:catalogObjectList', WARNING,
          'idxs is ignored in this function and is only provided to be compatible with CMFCatalogAware.reindexObject.')
    if not self.getPortalObject().isIndexable():
      return

    object_path_dict = {}
    uid_list = []
    uid_list_append = uid_list.append
    for object in object_list:
      if object in object_path_dict:
        continue
      path = object.getPath()
      if len(path) > MAX_PATH_LEN:
        raise  ValueError('path too long (%i): %r' % (len(path), path))
      object_path_dict[object] = path
      try:
        uid = aq_base(object).uid
      except AttributeError:
        uid = None
      if uid is None or uid == 0:
        object.uid = uid = self.newUid()
      uid_list_append(uid)
    LOG('SQLCatalog', TRACE, 'catalogging %d objects' % len(object_path_dict))
    if check_uid:
      path_uid_dict = self.getUidDictForPathList(path_list=object_path_dict.values())
      uid_path_dict = self.getPathDictForUidList(uid_list=uid_list)
      for object, path in object_path_dict.iteritems():
        uid = object.uid
        if path_uid_dict.setdefault(path, uid) != uid:
          error_message = 'path %r has uids %r (catalog) and %r (being indexed) ! This can break relations' % (
            path,
            path_uid_dict[path],
            uid,
          )
          if self.sql_catalog_raise_error_on_uid_check:
            raise ValueError(error_message)
          LOG("SQLCatalog._catalogObjectList", ERROR, error_message)
        catalog_path = uid_path_dict.setdefault(uid, path)
        if catalog_path != path and catalog_path != 'deleted':
          # Two possible cases if catalog_path == 'deleted':
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
          error_message = 'uid %r is shared between %r (catalog) and %r (being indexed) ! This can break relations' % (
            uid,
            catalog_path,
            path,
          )
          if self.sql_catalog_raise_error_on_uid_check:
            raise ValueError(error_message)
          LOG('SQLCatalog._catalogObjectList', ERROR, error_message)

    if method_id_list is None:
      method_id_list = self.getSqlCatalogObjectListList()
    econtext = getEngine().getContext()
    if disable_cache:
      argument_cache = DummyDict()
    else:
      argument_cache = {}

    with (noReadOnlyTransactionCache if disable_cache else
          readOnlyTransactionCache)():
      filter_dict = self._getFilterDict()
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
          catalogged_object_list = object_path_dict.keys()
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
            for object in object_path_dict:
              if expression_cache_key_list:
                # Expressions are slow to evaluate because they are executed
                # in restricted environment. So we try to save results of
                # expressions by portal_type or any other key.
                # This cache is built each time we reindex
                # objects but we could also use over multiple transactions
                # if this can improve performance significantly
                # ZZZ - we could find a way to compute this once only
                cache_key = tuple(object._getProperty(key) for key
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
        method = self._getCatalogMethod(method_name)
        kw = {
          x: LazyIndexationParameterList(
            catalogged_object_list,
            x,
            argument_cache,
          )
          for x in self._getCatalogMethodArgumentList(method)
        }
        try:
          method(**kw)
        except ConflictError:
          raise
        except:
          LOG(
            'SQLCatalog._catalogObjectList',
            ERROR,
            'could not catalog objects %s with method %s' % (
              object_list,
              method_name,
            ),
            error=True,
          )
          raise

  def _getCatalogMethodArgumentList(self, method):
    meta_type = method.meta_type
    if meta_type in self.HAS_ARGUMENT_SRC_METATYPE_SET:
      return method.arguments_src.split()
    elif meta_type in self.HAS_FUNC_CODE_METATYPE_SET:
      return method.func_code.co_varnames[:method.func_code.co_argcount]
    # Note: Raising here would completely prevent indexation from working.
    # Instead, let the method actually fail when called, so _catalogObjectList
    # can log the error and carry on.
    return ()

  def _getCatalogMethod(self, method_name):
    return getattr(self, method_name)

  def getSqlCatalogDeleteUid(self):
     return self.sql_catalog_delete_uid

  security.declarePrivate('beforeUncatalogObject')
  def beforeUncatalogObject(self, path=None,uid=None):
    """
    Set the path as deleted
    """
    if not self.getPortalObject().isIndexable():
      return None

    if uid is None and path is not None:
      uid = self.getUidForPath(path)
    method_name = self.getSqlCatalogDeleteUid()
    if uid is None:
      return None
    if method_name in (None,''):
      # This should exist only if the site is not up to date.
      LOG('ZSQLCatalog.beforeUncatalogObject', INFO, 'The sql_catalog_delete_uid method is not defined')
      return self.uncatalogObject(path=path,uid=uid)
    method = self._getOb(method_name)
    method(uid = uid)

  def getSqlUncatalogObjectList(self):
    return self.sql_uncatalog_object

  security.declarePrivate('uncatalogObject')
  def uncatalogObject(self, path=None, uid=None):
    """
    Uncatalog and object from the Catalog.

    Note, the uid must be the same as when the object was
    catalogued, otherwise it will not get removed from the catalog

    This method should not raise an exception if the uid cannot
    be found in the catalog.

    XXX Add filter of methods

    """
    if not self.getPortalObject().isIndexable():
      return None

    if uid is None and path is not None:
      uid = self.getUidForPath(path)
    method_id_list = self.getSqlUncatalogObjectList()
    if uid is None:
      return None
    for method_name in method_id_list:
      # Do not put try/except here, it is required to raise error
      # if uncatalog does not work.
      method = self._getOb(method_name)
      method(uid = uid)

  def getSqlCatalogTranslationList(self):
    return self.sql_catalog_translation_list

  security.declarePrivate('catalogTranslationList')
  def catalogTranslationList(self, object_list):
    """Catalog translations.
    """
    method_name = self.getSqlCatalogTranslationList()
    return self.catalogObjectList(object_list, method_id_list = (method_name,),
                                  check_uid=0)

  def getSqlDeleteTranslationList(self):
    return self.sql_delete_translation_list

  security.declarePrivate('deleteTranslationList')
  def deleteTranslationList(self):
    """Delete translations.
    """
    method_name = self.getSqlDeleteTranslationList()
    method = self._getOb(method_name)
    try:
      method()
    except ConflictError:
      raise
    except:
      LOG('SQLCatalog', WARNING, 'could not delete translations', error=True)

  def getSqlUniqueValues(self):
    return self.sql_unique_values

  security.declarePrivate('uniqueValuesFor')
  def uniqueValuesFor(self, name):
    """ return unique values for FieldIndex name """
    method = self._getOb(self.getSqlUniqueValues())
    return method(column=name)

  def getSqlCatalogPaths(self):
    return self.sql_catalog_paths

  security.declarePrivate('getPaths')
  def getPaths(self):
    """ Returns all object paths stored inside catalog """
    method = self._getOb(self.getSqlCatalogPaths())
    return method()

  def getSqlGetitemByPath(self):
    return self.sql_getitem_by_path

  security.declarePrivate('getUidForPath')
  def getUidForPath(self, path):
    """ Looks up into catalog table to convert path into uid """
    return self.getUidDictForPathList([path]).get(path)

  security.declarePrivate('getUidDictForPathList')
  def getUidDictForPathList(self, path_list):
    """ Looks up into catalog table to convert path into uid """
    return {
      x.path: x.uid
      for x in self._getOb(
        self.getSqlGetitemByPath()
      )(
        path=None, # BBB
        path_list=path_list,
        uid_only=False, # BBB
      )
    }

  security.declarePrivate('getPathDictForUidList')
  def getPathDictForUidList(self, uid_list):
    """ Looks up into catalog table to convert uid into path """
    return {
      x.uid: x.path
      for x in self._getOb(
        self.getSqlGetitemByUid()
      )(
        uid=None, # BBB
        uid_list=uid_list,
        path_only=False, # BBB
      )
    }

  security.declarePrivate('hasPath')
  def hasPath(self, path):
    """ Checks if path is catalogued """
    return self.getUidForPath(path) is not None

  security.declarePrivate('getPathForUid')
  def getPathForUid(self, uid):
    """ Looks up into catalog table to convert uid into path """
    return self.getPathDictForUidList([uid]).get(uid)

  security.declarePrivate('getMetadataForUid')
  def getMetadataForUid(self, uid):
    """ Accesses a single record for a given uid """
    result = {}
    path = self.getPathForUid(uid)
    if uid is not None:
      result['path'] = path
      result['uid'] = uid
    return result

  security.declarePrivate('getIndexDataForUid')
  def getIndexDataForUid(self, uid):
    """ Accesses a single record for a given uid """
    return self.getMetadataForUid(uid)

  security.declarePrivate('getMetadataForPath')
  def getMetadataForPath(self, path):
    """ Accesses a single record for a given path """
    result = {}
    uid = self.getUidForPath(path)
    if uid is not None:
      result['path'] = path
      result['uid'] = uid
    return result

  security.declarePrivate('getIndexDataForPath')
  def getIndexDataForPath(self, path):
    """ Accesses a single record for a given path """
    return self.getMetadataForPath(path)

  security.declarePrivate('getCatalogMethodIds')
  def getCatalogMethodIds(self,
                          valid_method_meta_type_list=('Z SQL Method',
                                                       'LDIF Method',
                                                       'Script (Python)')
                          ):
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

  security.declarePublic('getPythonMethodIds')
  def getPythonMethodIds(self):
    """
      Returns a list of all python scripts available in
      current sql catalog.
    """
    return self.getCatalogMethodIds(valid_method_meta_type_list=('Script (Python)', ))

  @transactional_cache_decorator
  def _getSQLCatalogRelatedKeySet(self):
    column_map = self.getColumnMap()
    column_set = set(column_map)
    for related_key in self.sql_catalog_related_keys:
      split_entire_definition = related_key.split('|')
      if len(split_entire_definition) != 2:
        LOG('SQLCatalog', WARNING, 'Malformed related key definition: %r. Ignored.' % (related_key, ))
        continue
      related_key_id = split_entire_definition[0].strip()
      if related_key_id in column_set and related_key_id not in related_key_warned_column_set:
        related_key_warned_column_set.add(related_key_id)
        if related_key_id in column_map:
          LOG('SQLCatalog', WARNING, 'Related key %r has the same name as an existing column on tables %r' % (related_key_id, column_map[related_key_id]))
        else:
          LOG('SQLCatalog', WARNING, 'Related key %r is declared more than once.' % (related_key_id, ))
      column_set.add(related_key_id)
    return column_set

  security.declarePrivate('getSQLCatalogRelatedKeyList')
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
  security.declarePrivate('getSqlCatalogRelatedKeyList')
  getSqlCatalogRelatedKeyList = getSQLCatalogRelatedKeyList

  security.declarePrivate('getSQLCatalogScriptableKeyList')
  def getSQLCatalogScriptableKeyList(self):
    """
    Return the list of scriptable keys.
    """
    return self.sql_catalog_scriptable_keys

  @transactional_cache_decorator
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

  security.declarePrivate('getTableIndex')
  def getTableIndex(self, table):
    """
    Return a map between index and column for a given table
    """
    return self._getTableIndex(table).copy()

  security.declareProtected(access_contents_information, 'isValidColumn')
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

  security.declarePrivate('getRelatedKeyDefinition')
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

  def getSqlCatalogKeywordSearchKeysList(self):
    return self.sql_catalog_keyword_search_keys

  def getSqlCatalogFullTextSearchKeysList(self):
    return self.sql_catalog_full_text_search_keys

  def getSqlCatalogDatetimeSearchKeysList(self):
    return self.sql_catalog_datetime_search_keys

  def getSqlCatalogScriptableKeysList(self):
    return self.sql_catalog_scriptable_keys

  @transactional_cache_decorator
  def _getgetScriptableKeyDict(self):
    result = {}
    for scriptable_key_definition in self.getSqlCatalogScriptableKeysList():
      split_scriptable_key_definition = scriptable_key_definition.split('|')
      if len(split_scriptable_key_definition) != 2:
        LOG('SQLCatalog', WARNING, 'Malformed scriptable key definition: %r. Ignored.' % (scriptable_key_definition, ))
        continue
      key, script_id = [x.strip() for x in split_scriptable_key_definition]
      script = getattr(self, script_id, None)
      if script is None:
        LOG('SQLCatalog', WARNING, 'Scriptable key %r script %r is missing. Skipped.' % (key, script_id))
      else:
        result[key] = script
    return result

  security.declarePrivate('getScriptableKeyScript')
  def getScriptableKeyScript(self, key):
    return self._getgetScriptableKeyDict().get(key)

  security.declarePrivate('getColumnSearchKey')
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
    # Is key a scriptable key, a related key or a "real" column ?
    script = self.getScriptableKeyScript(key)
    if script is None:
      related_key_definition = self.getRelatedKeyDefinition(key)
      if related_key_definition is None:
        if key in self.getColumnMap():
          search_key = self.getSearchKey(key, search_key_name)
        else:
          search_key = None
      else:
        search_key = self.getSearchKey(key, 'RelatedKey')
    else:
      search_key = SearchKeyWrapperForScriptableKey(key, script)
      related_key_definition = None
    return search_key, related_key_definition

  security.declarePrivate('hasColumn')
  def hasColumn(self, column):
    return self.getColumnSearchKey(column)[0] is not None

  security.declarePrivate('getColumnDefaultSearchKey')
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

  security.declareProtected(access_contents_information, 'buildSingleQuery')
  def buildSingleQuery(
    self,
    key,
    value,
    search_key_name=None,
    logical_operator=None,
    comparison_operator=None,
    ignore_unknown_columns=False,
  ):
    """
      From key and value, determine the SearchKey to use and generate a Query
      from it.
    """
    return self._buildQuery(
      buildQueryFromSearchKey=lambda search_key: search_key.buildQuery(
        value,
        logical_operator=logical_operator,
        comparison_operator=comparison_operator,
      ),
      key=key,
      search_key_name=search_key_name,
      ignore_unknown_columns=ignore_unknown_columns,
    )

  def _buildQueryFromAbstractSyntaxTreeNode(self, node, search_key, wrap, ignore_unknown_columns):
    """
    node
      Abstract syntax tree node (see SearchText/AdvancedSearchTextParser.py,
      classes inheriting from Node).
    search_key
      Search key to generate queries from values found during syntax tree walk.
    wrap
      Callback transforming a value just before it is passed to
      search_key.buildQuery .
    """
    if search_key.dequoteParsedText():
      _dequote = dequote
    else:
      _dequote = lambda x: x
    if node.isLeaf():
      result = search_key.buildQuery(wrap(_dequote(node.getValue())),
        comparison_operator=node.getComparisonOperator())
    elif node.isColumn():
      result = self.buildQueryFromAbstractSyntaxTreeNode(
        node.getSubNode(),
        node.getColumnName(),
        ignore_unknown_columns=ignore_unknown_columns,
      )
    else:
      query_list = []
      value_dict = {}
      append = query_list.append
      for subnode in node.getNodeList():
        if subnode.isLeaf():
          value_dict.setdefault(subnode.getComparisonOperator(),
            []).append(wrap(_dequote(subnode.getValue())))
        else:
          subquery = self._buildQueryFromAbstractSyntaxTreeNode(
            subnode,
            search_key,
            wrap,
            ignore_unknown_columns,
          )
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

  security.declareProtected(access_contents_information, 'buildQueryFromAbstractSyntaxTreeNode')
  def buildQueryFromAbstractSyntaxTreeNode(self, node, key, wrap=lambda x: x, ignore_unknown_columns=False):
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
    return self._buildQuery(
      buildQueryFromSearchKey=lambda search_key: self._buildQueryFromAbstractSyntaxTreeNode(
        node,
        search_key,
        wrap,
        ignore_unknown_columns,
      ),
      key=key,
      ignore_unknown_columns=ignore_unknown_columns,
    )

  def _buildQuery(self, buildQueryFromSearchKey, key, search_key_name=None, ignore_unknown_columns=False):
    """
      Determine the SearchKey to use to generate a Query, and call buildQueryFromSearchKey with it.
    """
    search_key, related_key_definition = self.getColumnSearchKey(key, search_key_name)
    if search_key is None:
      message = 'Unknown column ' + repr(key)
      if not ignore_unknown_columns:
        raise ValueError(message)
      # Unknown, skip loudly
      LOG('SQLCatalog', WARNING, message)
      result = None
    else:
      if related_key_definition is None:
        build_key = search_key
      else:
        build_key = search_key.getSearchKey(sql_catalog=self,
          related_key_definition=related_key_definition,
          search_key_name=search_key_name,
        )
      result = buildQueryFromSearchKey(search_key=build_key)
      if related_key_definition is not None:
        result = search_key.buildQuery(sql_catalog=self,
          related_key_definition=related_key_definition,
          search_value=result)
    return result

  def _parseSearchText(self, search_key, search_text, is_valid=None):
    if is_valid is None:
      is_valid = self.isValidColumn
    return search_key.parseSearchText(search_text, is_valid)

  security.declareProtected(access_contents_information, 'parseSearchText')
  def parseSearchText(self, search_text, column=None, search_key=None,
                      is_valid=None):
    if column is None and search_key is None:
      raise ValueError('One of column and search_key must be different from None')
    return self._parseSearchText(self.getSearchKey(
      column, search_key=search_key), search_text, is_valid=is_valid)

  security.declareProtected(access_contents_information, 'buildQuery')
  def buildQuery(self, kw, ignore_empty_string=True, operator='and', ignore_unknown_columns=False):
    query_list = []
    append = query_list.append
    # unknown_column_dict: contains all (key, value) pairs which could not be
    # changed into queries.
    unknown_column_dict = {}
    # empty_value_dict: contains all keys whose value causes them to be
    # discarded.
    empty_value_dict = {}
    for key, value in kw.iteritems():
      result = None
      if key in DOMAIN_STRICT_MEMBERSHIP_DICT:
        if value is None:
          continue
        value = self.getPortalObject().portal_selections.asDomainQuery(
          value,
          strict_membership=DOMAIN_STRICT_MEMBERSHIP_DICT[key],
        )
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
        if isinstance(value, BaseQuery):
          # Query instance: use as such, ignore key.
          result = value
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
              result = self.buildSingleQuery(
                key=key,
                value=raw_value,
                search_key_name=search_key_name,
                ignore_unknown_columns=ignore_unknown_columns,
              )
            else:
              result = self.buildQueryFromAbstractSyntaxTreeNode(
                abstract_syntax_tree, key, wrap,
                ignore_unknown_columns=ignore_unknown_columns,
              )
        else:
          # Any other type, just create a query. (can be a DateTime, ...)
          result = self.buildSingleQuery(
            key=key,
            value=value,
            ignore_unknown_columns=ignore_unknown_columns,
          )
        if result is None:
          # No query could be created, emit a log, add to unknown column dict.
          unknown_column_dict[key] = value
        else:
          append(result)
    if len(empty_value_dict):
      LOG('SQLCatalog', WARNING, 'Discarding columns with empty values: %r' % (empty_value_dict, ))
    if len(unknown_column_dict):
      message = 'Unknown columns ' + repr(unknown_column_dict.keys())
      if ignore_unknown_columns:
        LOG('SQLCatalog', WARNING, message)
      else:
        raise TypeError(message)
    return ComplexQuery(query_list, logical_operator=operator)

  security.declarePrivate('buildOrderByList')
  def buildOrderByList(self, sort_on=None, sort_order=None):
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
          if item[1] in ('descending', 'reverse', 'desc', 'DESC'):
            item[1] = 'DESC'
          else:
            item[1] = 'ASC'
          if len(item) > 2:
            if item[2] == 'int':
              item[2] = 'SIGNED'
            elif item[2] == 'float':
              item[2] = 'DECIMAL'
        append(item)
    return order_by_list

  security.declarePrivate('buildEntireQuery')
  def buildEntireQuery(self, kw,
                       query_table='catalog',
                       query_table_alias=None,
                       ignore_empty_string=1,
                       limit=None, extra_column_list=(),
                       ignore_unknown_columns=False):
    kw = self.getCannonicalArgumentDict(kw)
    group_by_list = kw.pop('group_by_list', [])
    select_dict = kw.pop('select_dict', {})
    # Handle left_join_list
    left_join_list = kw.pop('left_join_list', ())
    inner_join_list = kw.pop('inner_join_list', ())
    # Handle implicit_join. It's True by default, as there's a lot of code
    # in BT5s and elsewhere that calls buildSQLQuery() expecting implicit
    # join. self._queryResults() defaults it to False for those using
    # catalog.searchResults(...) or catalog(...) directly.
    implicit_join = kw.pop('implicit_join', True)
    # Handle order_by_list
    order_by_list = kw.pop('order_by_list', [])
    return EntireQuery(
      query=self.buildQuery(kw, ignore_empty_string=ignore_empty_string, ignore_unknown_columns=ignore_unknown_columns),
      order_by_list=order_by_list,
      group_by_list=group_by_list,
      select_dict=select_dict,
      left_join_list=left_join_list,
      inner_join_list=inner_join_list,
      implicit_join=implicit_join,
      limit=limit,
      catalog_table_name=query_table,
      catalog_table_alias=query_table_alias,
      extra_column_list=extra_column_list,
    )

  security.declarePublic('buildSQLQuery')
  def buildSQLQuery(self, query_table='catalog',
                          query_table_alias=None,
                          REQUEST=None,
                          ignore_empty_string=1, only_group_columns=False,
                          limit=None, extra_column_list=(),
                          ignore_unknown_columns=False,
                          **kw):
    return self.buildEntireQuery(
      kw,
      query_table=query_table,
      query_table_alias=query_table_alias,
      ignore_empty_string=ignore_empty_string,
      limit=limit,
      extra_column_list=extra_column_list,
      ignore_unknown_columns=ignore_unknown_columns,
    ).asSQLExpression(
      self,
      only_group_columns,
    ).asSQLExpressionDict()

  # Compatibililty SQL Sql
  security.declarePrivate('buildSqlQuery')
  buildSqlQuery = buildSQLQuery

  security.declareProtected(access_contents_information, 'getCannonicalArgumentDict')
  def getCannonicalArgumentDict(self, kw):
    """
    Convert some catalog arguments to generic arguments.

    group_by -> group_by_list
    select_list -> select_dict
    sort_on, sort_on_order -> order_list
    """
    kw = kw.copy()

    kw['group_by_list'] = kw.pop('group_by_list', None) or kw.pop('group_by', [])

    select_dict = kw.pop('select_dict', None) or kw.pop('select_list', {})
    if isinstance(select_dict, (list, tuple)):
      select_dict = dict.fromkeys(select_dict)
    kw['select_dict'] = select_dict

    order_by_list = kw.pop('order_by_list', None)
    sort_on = kw.pop('sort_on', None)
    sort_order = kw.pop('sort_order', None)
    if order_by_list is None:
      order_by_list = self.buildOrderByList(
        sort_on=sort_on,
        sort_order=sort_order,
      )
    else:
      if sort_on is not None:
        LOG('SQLCatalog', WARNING, 'order_by_list and sort_on were given, ignoring sort_on.')
      if sort_order is not None:
        LOG('SQLCatalog', WARNING, 'order_by_list and sort_order were given, ignoring sort_order.')
    kw['order_by_list'] = order_by_list or []
    return kw

  def getSqlCatalogSearchKeysList(self):
    return self.sql_catalog_search_keys

  @transactional_cache_decorator
  def _getSearchKeyDict(self):
    result = {}
    search_key_column_dict = {
      'KeywordKey': self.getSqlCatalogKeywordSearchKeysList(),
      'FullTextKey': self.getSqlCatalogFullTextSearchKeysList(),
      'DateTimeKey': self.getSqlCatalogDatetimeSearchKeysList(),
    }
    for key, column_list in search_key_column_dict.iteritems():
      for column in column_list:
        if column in result:
          LOG('SQLCatalog', WARNING, 'Ambiguous configuration: column %r is set to use %r key, but also to use %r key. Former takes precedence.' % (column, result[column], key))
        else:
          result[column] = key
    for line in self.getSqlCatalogSearchKeysList():
      try:
        column, key = [x.strip() for x in line.split('|', 2)]
        result[column] = key
      except ValueError:
        LOG('SQLCatalog', WARNING, 'Wrong configuration for sql_catalog_search_keys: %r' % line)
    return result

  security.declarePrivate('getSearchKey')
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

  security.declarePrivate('getComparisonOperator')
  def getComparisonOperator(self, operator):
    """
      Return an instance of an Operator class.

      operator (string)
        String defining the expected operator class.
        See Operator module to have a list of available operators.
    """
    return getComparisonOperatorInstance(operator)


  security.declarePrivate('queryResults')
  def queryResults(
        self,
        sql_method,
        REQUEST=None,
        src__=0,
        build_sql_query_method=None,
        # XXX should get zsql_brain from ZSQLMethod class itself
        zsql_brain=None,
        implicit_join=False,
        query_timeout=None,
        **kw
      ):
    if build_sql_query_method is None:
      build_sql_query_method = self.buildSQLQuery
    query = build_sql_query_method(
      REQUEST=REQUEST,
      implicit_join=implicit_join,
      **kw
    )
    return sql_method(
      src__=src__,
      zsql_brain=zsql_brain,
      selection_domain=None, # BBB
      selection_report=None, # BBB
      where_expression=query['where_expression'],
      select_expression=query['select_expression'],
      group_by_expression=query['group_by_expression'],
      from_table_list=query['from_table_list'],
      from_expression=query['from_expression'],
      sort_on=query['order_by_expression'],
      limit_expression=query['limit_expression'],
      query_timeout=query_timeout,
    )

  def getSqlSearchResults(self):
    return self.sql_search_results

  security.declarePrivate('getSearchResultsMethod')
  def getSearchResultsMethod(self):
    return self._getOb(self.getSqlSearchResults())

  security.declarePrivate('searchResults')
  def searchResults(self, REQUEST=None, **kw):
    """ Returns a list of brains from a set of constraints on variables """
    if 'only_group_columns' in kw:
      # searchResults must be consistent in API with countResults
      raise ValueError(
        'only_group_columns does not belong to this API level, use queryResults directly',
      )
    return self.queryResults(
      self.getSearchResultsMethod(),
      REQUEST=REQUEST,
      extra_column_list=self.getCatalogSearchResultKeys(),
      **kw
    )

  __call__ = searchResults

  def getSqlCountResults(self):
    return self.sql_count_results

  security.declarePrivate('getCountResultsMethod')
  def getCountResultsMethod(self):
    return self._getOb(self.getSqlCountResults())

  security.declarePrivate('countResults')
  def countResults(self, REQUEST=None, **kw):
    """ Returns the number of items which satisfy the conditions """
    return self.queryResults(
      self.getCountResultsMethod(),
      REQUEST=REQUEST,
      extra_column_list=self.getCatalogSearchResultKeys(),
      only_group_columns=True,
      **kw
    )

  security.declarePrivate('isAdvancedSearchText')
  def isAdvancedSearchText(self, search_text):
    return isAdvancedSearchText(search_text, self.isValidColumn)

  def getSqlRecordObjectList(self):
    return self.sql_record_object_list

  security.declarePrivate('recordObjectList')
  def recordObjectList(self, path_list, catalog=1):
    """
      Record the path of an object being catalogged or uncatalogged.
    """
    method = self._getOb(self.getSqlRecordObjectList())
    method(path_list=path_list, catalog=catalog)

  def getSqlDeleteRecordedObjectList(self):
    return self.sql_delete_recorded_object_list

  security.declarePrivate('deleteRecordedObjectList')
  def deleteRecordedObjectList(self, uid_list=()):
    """
      Delete all objects which contain any path.
    """
    method = self._getOb(self.getSqlDeleteRecordedObjectList())
    method(uid_list=uid_list)

  def getSqlReadRecordedObjectList(self):
    return self.sql_read_recorded_object_list

  security.declarePrivate('readRecordedObjectList')
  def readRecordedObjectList(self, catalog=1):
    """
      Read objects. Note that this might not return all objects since ZMySQLDA limits the max rows.
    """
    method = self._getOb(self.getSqlReadRecordedObjectList())
    return method(catalog=catalog)

  security.declarePublic('getConnectionId')
  def getConnectionId(self, deferred=False):
    """
    Returns the 'normal' connection being used by the SQL Method(s) in this
    catalog.
    If 'deferred' is True, then returns the deferred connection
    """
    for method in self.objectValues():
      if method.meta_type in ('Z SQL Method', 'ERP5 SQL Method') and ('deferred' in method.connection_id) == deferred:
        return method.connection_id

  def getSqlCatalogObjectList(self):
    try:
      return self.sql_catalog_object
    except AttributeError:
      return ()

  def getSqlUncatalogObjectList(self):
    try:
      return self.sql_uncatalog_object
    except AttributeError:
      return ()

  def getSqlUpdateObjectList(self):
    try:
      return self.sql_update_object
    except AttributeError:
      return ()

  def getSqlCatalogObjectListList(self):
    try:
      return self.sql_catalog_object_list
    except AttributeError:
      return ()

  security.declarePrivate('getFilterableMethodList')
  def getFilterableMethodList(self):
    """
    Returns only zsql methods wich catalog or uncatalog objets
    """
    method_id_set = set()
    if withCMF:
      method_id_set.update(
        self.getSqlCatalogObjectList() +
        self.getSqlUncatalogObjectList() +
        self.getSqlUpdateObjectList() +
        self.getSqlCatalogObjectListList()
      )
    return [
      method
      for method in (
        getattr(self, method_id, None)
        for method_id in method_id_set
      )
      if method is not None
    ]

  security.declarePrivate('getExpressionContext')
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
            #'user':         getSecurityManager().getUser().getIdOrUserName(),
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

  def _getOptimizerSwitch(self):
    method_name = self.sql_optimizer_switch
    try:
      method = getattr(self, method_name)
    except AttributeError:
      pass
    else:
      try:
        return method()[0][0]
      except (ConflictError, DatabaseError):
        raise
      except Exception:
        pass
    LOG(
      'SQLCatalog',
      WARNING,
      'getTableIds failed with the method %s' % method_name,
      error=True,
    )
    return ''

  security.declarePublic('getOptimizerSwitchKeyList')
  @transactional_cache_decorator
  def getOptimizerSwitchKeyList(self):
    return [
      pair.split('=', 1)[0]
      for pair in self._getOptimizerSwitch().split(',')
    ]

InitializeClass(Catalog)

class CatalogError(Exception): pass

from Query.Query import Query as BaseQuery
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
  def __init__(self, column, script):
    self.script = script
    super(SearchKeyWrapperForScriptableKey, self).__init__(column)

  def buildQuery(self, search_value, group=None, logical_operator=None,
                 comparison_operator=None):
    # XXX: It would be better to extend ScriptableKey API to support other
    # parameters.
    if group is not None:
      raise ValueError(
        'ScriptableKey cannot be used inside a group (%r given).' % (group, ),
      )
    if logical_operator is not None:
      raise ValueError(
        'ScriptableKey ignores logical operators (%r given).' % (logical_operator, ),
      )
    if comparison_operator:
      raise ValueError(
        'ScriptableKey ignores comparison operators (%r given).' % (comparison_operator, ),
      )
    return self.script(search_value)

from Operator import operator_dict
def getComparisonOperatorInstance(operator):
  return operator_dict[operator]

from Query.EntireQuery import EntireQuery

verifyClass(ISearchKeyCatalog, Catalog)
