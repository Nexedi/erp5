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
from Globals import DTMLFile, PersistentMapping
from string import lower, split, join
from thread import get_ident
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo, getSecurityManager
from BTrees.OIBTree import OIBTree

from DateTime import DateTime
from Products.PluginIndexes.common.randid import randid
from Acquisition import aq_parent, aq_inner, aq_base, aq_self
from zLOG import LOG

import time
import sys
import urllib
import string
from cStringIO import StringIO
from xml.dom.minidom import parse, parseString, getDOMImplementation
from xml.sax.saxutils import escape, quoteattr

try:
  from Products.PageTemplates.Expressions import SecureModuleImporter
  from Products.CMFCore.Expression import Expression
  from Products.PageTemplates.Expressions import getEngine
  from Products.CMFCore.utils import getToolByName
  withCMF = 1
except ImportError:
  withCMF = 0


UID_BUFFER_SIZE = 900
MAX_UID_BUFFER_SIZE = 20000

valid_method_meta_type_list = ('Z SQL Method', 'Script (Python)')

manage_addSQLCatalogForm=DTMLFile('dtml/addSQLCatalog',globals())

def manage_addSQLCatalog(self, id, title,
             vocab_id='create_default_catalog_',
             REQUEST=None):
  """Add a Catalog object
  """
  id=str(id)
  title=str(title)
  vocab_id=str(vocab_id)
  if vocab_id == 'create_default_catalog_':
    vocab_id = None

  c=Catalog(id, title, self)
  self._setObject(id, c)
  if REQUEST is not None:
    return self.manage_main(self, REQUEST,update_menu=1)


class Catalog(Folder, Persistent, Acquisition.Implicit, ExtensionClass.Base):
  """ An Object Catalog

  An Object Catalog maintains a table of object metadata, and a
  series of manageable indexes to quickly search for objects
  (references in the metadata) that satisfy a search where_expression.

  This class is not Zope specific, and can be used in any python
  program to build catalogs of objects.  Note that it does require
  the objects to be Persistent, and thus must be used with ZODB3.

  uid -> the (local) universal ID of objects
  path -> the (local) path of objects


  bgrain defined in meyhods...

  TODO:

    - optmization: indexing objects should be deferred
      until timeout value or end of transaction
  """
  meta_type = "SQLCatalog"
  icon='misc_/ZCatalog/ZCatalog.gif' # FIXME: use a different icon
  security = ClassSecurityInfo()

  manage_options = (
    {'label': 'Contents',       # TAB: Contents
     'action': 'manage_main',
     'help': ('OFSP','ObjectManager_Contents.stx')},
    {'label': 'Catalog',      # TAB: Catalogged Objects
     'action': 'manage_catalogView',
     'target': 'manage_main',
     'help':('ZCatalog','ZCatalog_Cataloged-Objects.stx')},
    {'label': 'Properties',     # TAB: Properties
     'action': 'manage_propertiesForm',
     'help': ('OFSP','Properties.stx')},
    {'label': 'Filter',     # TAB: Filter
     'action': 'manage_catalogFilter',},
    {'label': 'Find Objects',     # TAB: Find Objects
     'action': 'manage_catalogFind',
     'target':'manage_main',
     'help':('ZCatalog','ZCatalog_Find-Items-to-ZCatalog.stx')},
    {'label': 'Advanced',       # TAB: Advanced
     'action': 'manage_catalogAdvanced',
     'target':'manage_main',
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
    )

  __ac_permissions__=(

    ('Manage ZCatalog Entries',
     ['manage_catalogObject', 'manage_uncatalogObject',

      'manage_catalogView', 'manage_catalogFind',
      'manage_catalogSchema', 'manage_catalogFilter',
      'manage_catalogAdvanced', 'manage_objectInformation',

      'manage_catalogReindex', 'manage_catalogFoundItems',
      'manage_catalogClear', 'manage_editSchema',
      'manage_reindexIndex', 'manage_main',
      'manage_editFilter',

      'manage_exportProperties', 'manage_importProperties',

      ],
     ['Manager']),

    ('Search ZCatalog',
     ['searchResults', '__call__', 'uniqueValuesFor',
      'getpath', 'schema', 'names', 'columns', 'indexes', 'index_objects',
      'all_meta_types', 'valid_roles', 'resolve_url',
      'getobject', 'getObject', 'getObjectList', 'getCatalogSearchTableIds',
      'getCatalogSearchResultKeys', 'getFilterableMethodList', ],
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
    { 'id'      : 'sql_catalog_object',
      'description' : 'Methods to be called to catalog an object',
      'type'    : 'multiple selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_uncatalog_object',
      'description' : 'Methods to be called to uncatalog an object',
      'type'    : 'multiple selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_update_object',
      'description' : 'Methods will be called to updat a catalogued object',
      'type'    : 'multiple selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_clear_catalog',
      'description' : 'The methods which should be called to clear the catalog',
      'type'    : 'multiple selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_object_list',
      'description' : 'Methods to be called to catalog the list of objects',
      'type'    : 'multiple selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_record_catalog_object',
      'description' : 'Method to record catalog information',
      'type'    : 'selection',
      'select_variable' : 'getCatalogMethodIds',
      'mode'    : 'w' },
    { 'id'      : 'sql_record_uncatalog_object',
      'description' : 'Method to record uncatalog information',
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
    { 'id'      : 'sql_catalog_topic_search_keys',
      'description' : 'Columns which should be considered as topic index',
      'type'    : 'lines',
      'mode'    : 'w' },
    { 'id'      : 'sql_catalog_related_keys',
      'title'   : 'Related keys',
      'description' : 'Additional columns obtained through joins',
      'type'    : 'lines',
      'mode'    : 'w' },
  )

  sql_catalog_produce_reserved = 'z_produce_reserved_uid_list'
  sql_catalog_clear_reserved = 'z_clear_reserved'
  sql_catalog_object = ('z_catalog_object',)
  sql_uncatalog_object = ('z_uncatalog_object',)
  sql_update_object = ('z_update_object',)
  sql_clear_catalog = ('z_drop_catalog', 'z_create_catalog')
  sql_catalog_object_list = ('z_catalog_object_list',)
  sql_record_catalog_object = 'z_record_catalog_object'
  sql_record_uncatalog_object = 'z_record_uncatalog_object'
  sql_read_recorded_object_list = 'z_read_recorded_object_list'
  sql_delete_recorded_object_list = 'z_delete_recorded_object_list'
  sql_search_results = 'z_search_results'
  sql_count_results = 'z_count_results'
  sql_getitem_by_path = 'z_getitem_by_path'
  sql_getitem_by_uid = 'z_getitem_by_uid'
  sql_catalog_tables = 'z_catalog_tables'
  sql_search_tables = ('catalog',)
  sql_catalog_schema = 'z_catalog_schema'
  sql_unique_values = 'z_unique_values'
  sql_catalog_paths = 'z_catalog_paths'
  sql_catalog_keyword_search_keys =  ('Description', 'Title', 'SearchableText')
  sql_catalog_full_text_search_keys = ()
  sql_catalog_request_keys = ()
  sql_search_result_keys = ()
  sql_catalog_topic_search_keys = ()
  sql_catalog_multivalue_keys = ()
  sql_catalog_related_keys = ()

  _after_clear_reserved = 0

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

  def manage_exportProperties(self, REQUEST=None, RESPONSE=None):
    """
      Export properties to an XML file.
    """
    f = StringIO()
    f.write('<?xml version="1.0"?>\n<SQLCatalogData>\n')
    id_list = self.propertyIds()
    for id in id_list:
      value = self.getProperty(id)

      if value is None:
        # What is this? Not used?
        continue

      if type(value) == type(""):
        f.write('  <property id=%s type="str">%s</property>\n' % (quoteattr(id), escape(value)))
      elif type(value) == type(()):
        f.write('  <property id=%s type="tuple">\n' % quoteattr(id))
        for item in value:
          if type(item) == type(""):
            f.write('    <item type="str">%s</item>\n' % escape(item))
          else:
            # Ignore the other types at the moment.
            pass
        f.write('  </property>\n')
      else:
        # Ignore the other types at the moment.
        pass
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
            raise CatalogError, 'unknown property id %r' (id,)
          if type not in ('str', 'tuple'):
            raise CatalogError, 'unknown property type %r' (type,)
          if type == 'str':
            value = ''
            for text in prop.childNodes:
              if text.nodeType == text.TEXT_NODE:
                value = text.data
                break
          else:
            value = []
            for item in prop.getElementsByTagName("item"):
              item_type = item.getAttribute("type")
              if item_type != 'str':
                raise CatalogError, 'unknown item type %r' (item_type,)
              for text in item.childNodes:
                if text.nodeType == text.TEXT_NODE:
                  value.append(text.data)
                  break
            value = tuple(value)

          setattr(self, id, value)
      finally:
        doc.unlink()
    finally:
      f.close()

  def _clearSecurityCache(self):
    self.security_uid_dict = OIBTree()
    self.security_uid_index = 0

  security.declarePrivate('getSecurityUid')
  def getSecurityUid(self, object):
    """
      Cache a uid for each security permission

      We try to create a unique security (to reduce number of lines)
      and to assign security only to root document
    """
    # Get security information
    allowed_roles_and_users = object.allowedRolesAndUsers()
    # Sort it
    allowed_roles_and_users = list(allowed_roles_and_users)
    allowed_roles_and_users.sort()
    allowed_roles_and_users = tuple(allowed_roles_and_users)
    # Make sure no diplicates
    if not hasattr(aq_base(self), 'security_uid_dict'):
      self._clearSecurityCache()
    if self.security_uid_dict.has_key(allowed_roles_and_users):
      return (self.security_uid_dict[allowed_roles_and_users], None)
    self.security_uid_index = self.security_uid_index + 1
    self.security_uid_dict[allowed_roles_and_users] = self.security_uid_index
    return (self.security_uid_index, allowed_roles_and_users)

  def clear(self):
    """
    Clears the catalog by calling a list of methods
    """
    methods = self.sql_clear_catalog
    for method_name in methods:
      method = getattr(self,method_name)
      try:
        method()
      except:
        LOG('SQLCatalog Warning: could not clear catalog', 0, method_name, error=sys.exc_info())
        pass

    # Remove the cache of catalog schema.
    if hasattr(self, '_v_catalog_schema_dict') :
      del self._v_catalog_schema_dict
    
    self._clearSecurityCache()

  def clearReserved(self):
    """
    Clears reserved uids
    """
    method_id = self.sql_catalog_clear_reserved
    method = getattr(self, method_id)
    method()
    self._after_clear_reserved = 1

  def __getitem__(self, uid):
    """
    Get an object by UID
    Note: brain is defined in Z SQL Method object
    """
    method = getattr(self,  self.sql_getitem_by_uid)
    search_result = method(uid = uid)
    if len(search_result) > 0:
      return search_result[0]
    else:
      return None

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

  def _getCatalogSchema(self, table=None):
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
      except:
        LOG('WARNING SQLCatalog._getCatalogSchema failed with the method', 0, method_name, error=sys.exc_info())
        pass
      catalog_schema_dict[table] = tuple(result_list)
      self._v_catalog_schema_dict= catalog_schema_dict
      
    return catalog_schema_dict[table]
      
  def getColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids

    XXX This should be cached
    """
    keys = {}
    for table in self.getCatalogSearchTableIds():
      field_list = self._getCatalogSchema(table=table)
      for field in field_list:
        keys[field] = 1
        keys['%s.%s' % (table, field)] = 1  # Is this inconsistent ?
    keys = keys.keys()
    keys.sort()
    return keys

  def getColumnMap(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids

    XXX This should be cached
    """
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
    except:
      pass
    return keys

  # the cataloging API
  def produceUid(self):
    """
      Produces reserved uids in advance
    """
    method_id = self.sql_catalog_produce_reserved
    method = getattr(self, method_id)
    thread_id = get_ident()
    uid_list = getattr(self, '_v_uid_buffer', [])
    if self._after_clear_reserved:
      # Reset uid list after clear reserved
      self._after_clear_reserved = 0
      uid_list = []
    if len(uid_list) < UID_BUFFER_SIZE:
      date = DateTime()
      new_uid_list = method(count = UID_BUFFER_SIZE, thread_id=thread_id, date=date)
      uid_list.extend( filter(lambda x: x != 0, map(lambda x: x.uid, new_uid_list )))
    self._v_uid_buffer = uid_list

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
    self.produceUid()
    uid_list = getattr(self, '_v_uid_buffer', [])
    if len(uid_list) > 0:
      return uid_list.pop()
    else:
      raise CatalogError("Could not retrieve new uid")

  def manage_catalogObject(self, REQUEST, RESPONSE, URL1, urls=None):
    """ index Zope object(s) that 'urls' point to """
    if urls:
      if isinstance(urls, types.StringType):
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
      if isinstance(urls, types.StringType):
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

  def manage_catalogClear(self, REQUEST=None, RESPONSE=None, URL1=None, sql_catalog_id=None):
    """ clears the whole enchilada """
    self.clear()

    if RESPONSE and URL1:
      RESPONSE.redirect(URL1 + '/manage_catalogAdvanced?manage_tabs_message=Catalog%20Cleared')

  def manage_catalogClearReserved(self, REQUEST=None, RESPONSE=None, URL1=None):
    """ clears the whole enchilada """
    self.clearReserved()

    if RESPONSE and URL1:
      RESPONSE.redirect(URL1 + '/manage_catalogAdvanced?manage_tabs_message=Catalog%20Cleared')

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
    """
    Adds an object to the Catalog by calling
    all SQL methods and providing needed arguments.

    'object' is the object to be cataloged

    'uid' is the unique Catalog identifier for this object

    """
    #LOG('catalogObject', 0, 'object = %r, path = %r' % (object, path))
    if withCMF:
      zope_root = getToolByName(self, 'portal_url').getPortalObject().aq_parent
    else:
      zope_root = self.getPhysicalRoot()

    root_indexable = int(getattr(zope_root,'isIndexable',1))

    # Prepare the dictionnary of values
    kw = {}

    # Check if already Catalogued
    if hasattr(aq_base(object), 'uid'):
      # Try to use existing uid
      # WARNING COPY PASTE....
      uid = object.uid
    else:
      # Look up in (previous) path
      uid = 0
    if is_object_moved:
      index = uid # We trust the current uid
    else:
      index = self.getUidForPath(path)
    if index:
      if (uid != index):
        # The new database must not change the uid.
        if self.hot_reindexing_state is not None and self.destination_sql_catalog_id == self.id:
          self.uncatalogObject(path)
          self.catalog_object(object, path, is_object_moved=is_object_moved,
                              sql_catalog_id=self.source_sql_catalog_id)
          return self.catalogObject(object, path, is_object_moved=is_object_moved)
        # Update uid attribute of object
        uid = int(index)
        #LOG("Write Uid",0, "uid %s index %s" % (uid, index))
        object.uid = uid
      # We will check if there is an filter on this
      # method, if so we may not call this zsqlMethod
      # for this object
      methods = self.sql_update_object
      for method_name in methods:
        if self.isMethodFiltered(method_name):
          if self.filter_dict.has_key(method_name):
            portal_type = object.getPortalType()
            if portal_type not in (self.filter_dict[method_name]['type']):
              #LOG('catalog_object',0,'XX1 this method is broken because not in types: %s' % method_name)
              continue
            else:
              expression = self.filter_dict[method_name]['expression_instance']
              if expression is not None:
                econtext = self.getExpressionContext(object)
                result = expression(econtext)
                if not result:
                  #LOG('catalog_object',0,'XX2 this method is broken because expression: %s' % method_name)
                  continue
        #LOG('catalog_object',0,'this method is not broken: %s' % method_name)
        # Get the appropriate SQL Method
        # Lookup by path is required because of OFS Semantics
        method = getattr(self, method_name)
        if method.meta_type == "Z SQL Method":
          # Build the dictionnary of values
          arguments = method.arguments_src
          for arg in split(arguments):
            try:
              value = getattr(object, arg, None)
              if callable(value):
                value = value()
              kw[arg] = value
            except:
              LOG("SQLCatalog Warning: Callable value could not be called",0,str((path, arg, method_name)))
              kw[arg] = None
        method = aq_base(method).__of__(object.__of__(self)) # Use method in the context of object
        # Generate UID
        kw['path'] = path
        kw['uid'] = int(index)
        kw['insert_catalog_line'] = 0
        #LOG("SQLCatalog Warning: insert_catalog_line, case1 value",0,0)
        # LOG
        # LOG("Call SQL Method %s with args:" % method_name,0, str(kw))
        # Alter row
        #LOG("Call SQL Method %s with args:" % method_name,0, str(kw))
        try:
          if root_indexable:
            #LOG("Call SQL Method %s with args:" % method_name,0, str(kw))
            method(**kw)
        except:
          LOG("SQLCatalog Warning: could not catalog object with method %s" % method_name,100, str(path))
          raise
    else:
      # Get the appropriate SQL Method
      # Lookup by path is required because of OFS Semantics
      if uid:
        # Make sure no duplicates - ie. if an object with different path has same uid, we need a new uid
        # This can be very dangerous with relations stored in a category table (CMFCategory)
        # This is why we recommend completely reindexing subobjects after any change of id
        catalog_path = self.getPathForUid(uid)
        if catalog_path == "reserved":
          # Reserved line in catalog table
          insert_catalog_line = 0
          #LOG("SQLCatalog Warning: insert_catalog_line, case2",0,insert_catalog_line)
        elif catalog_path is None:
          # No line in catalog table
          insert_catalog_line = 1
          #LOG("SQLCatalog Warning: insert_catalog_line, case3",0,insert_catalog_line)
        else:
          #LOG('SQLCatalog WARNING',0,'assigning new uid to already catalogued object %s' % path)
          uid = 0
          insert_catalog_line = 0
          #LOG("SQLCatalog Warning: insert_catalog_line, case4",0,insert_catalog_line)
      if not uid:
        # Generate UID
        index = self.newUid()
        object.uid = index
        insert_catalog_line = 0
        #LOG("SQLCatalog Warning: insert_catalog_line, case5",0,insert_catalog_line)
      else:
        index = uid
      methods = self.sql_catalog_object
      for method_name in methods:
        # We will check if there is an filter on this
        # method, if so we may not call this zsqlMethod
        # for this object
        if self.isMethodFiltered(method_name):
          if self.filter_dict.has_key(method_name):
            portal_type = object.getPortalType()
            if portal_type not in (self.filter_dict[method_name]['type']):
              #LOG('catalog_object',0,'XX1 this method is broken because not in types: %s' % method_name)
              continue
            else:
              expression = self.filter_dict[method_name]['expression_instance']
              if expression is not None:
                econtext = self.getExpressionContext(object)
                result = expression(econtext)
                if not result:
                  #LOG('catalog_object',0,'XX2 this method is broken because expression: %s' % method_name)
                  continue
        #LOG('catalog_object',0,'this method is not broken: %s' % method_name)

        method = getattr(self, method_name)
        if method.meta_type == "Z SQL Method":
          # Build the dictionnary of values
          arguments = method.arguments_src
          for arg in split(arguments):
            try:
              value = getattr(object, arg, None)
              if callable(value):
                value = value()
              kw[arg] = value
            except:
              kw[arg] = None
              LOG("SQLCatalog Warning: Callable value could not be called",0,str((path, arg, method_name)))
        try:
          method = aq_base(method).__of__(object.__of__(self)) # Use method in the context of object
        except AttributeError:
          LOG('SQLCatalog Warning, can not find method for object',0,(method,object))
          continue
        # Generate UID
        kw['path'] = path
        kw['uid'] = index
        kw['insert_catalog_line'] = insert_catalog_line
        # Alter/Create row
        try:
          if root_indexable:
            #LOG("No Index, Call SQL Method %s with args:" % method_name,0, str(kw))
            method(**kw)
        except:
          LOG("SQLCatalog Warning: could not catalog object with method %s" % method_name,100, str(path), error=sys.exc_info())
          raise
        #except:
        #  #  # This is a real LOG message
        #  #  # which is required in order to be able to import .zexp files
        #  LOG("SQLCatalog Warning: could not catalog object with method %s" % method_name,
        #                                                                   100,str(path))

  # XXX It is better to merge this with catalogObject. Too much code duplication.
  def catalogObjectList(self, object_list):
    """
      Add objects to the Catalog by calling
      all SQL methods and providing needed arguments.

      Each element of 'object_list' is an object to be cataloged

      'uid' is the unique Catalog identifier for this object

      WARNING: This method assumes that currently all objects are being reindexed from scratch.

      XXX: For now newUid is used to allocated UIDs. Is this good? Is it better to INSERT then SELECT?
    """
    if withCMF:
      zope_root = getToolByName(self, 'portal_url').getPortalObject().aq_parent
    else:
      zope_root = self.getPhysicalRoot()

    root_indexable = int(getattr(zope_root,'isIndexable',1))
    if not root_indexable:
      return

    for object in object_list:
      if getattr(aq_base(object), 'uid',None) is None:
        try:
          object._setUid(self.newUid())
        except:
          raise RuntimeError, 'could not set missing uid fro %r' % (object,)

    methods = self.sql_catalog_object_list
    for method_name in methods:
      kw = {}
      #LOG('catalogObjectList', 0, 'method_name = %s, self.isMethodFiltered(method_name) = %r, self.filter_dict.has_key(method_name) = %r' % (method_name, self.isMethodFiltered(method_name), self.filter_dict.has_key(method_name)))
      if self.isMethodFiltered(method_name) and self.filter_dict.has_key(method_name):
        catalogged_object_list = []
        type_list = self.filter_dict[method_name]['type']
        expression = self.filter_dict[method_name]['expression_instance']
        #LOG('catalogObjectList', 0, 'method_name = %s, type_list = %r, expression = %r' % (method_name, type_list, expression))
        for object in object_list:
          # We will check if there is an filter on this
          # method, if so we may not call this zsqlMethod
          # for this object
          portal_type = object.getPortalType()
          if portal_type not in type_list:
            continue
          elif expression is not None:
              econtext = self.getExpressionContext(object)
              result = expression(econtext)
              if not result:
                continue
          catalogged_object_list.append(object)
      else:
        catalogged_object_list = object_list

      if len(catalogged_object_list) == 0:
        continue

      #LOG('catalogObjectList', 0, 'method_name = %s' % (method_name,))
      method = getattr(self, method_name)
      if method.meta_type == "Z SQL Method":
        # Build the dictionnary of values
        arguments = method.arguments_src
        for arg in split(arguments):
          value_list = []
          for object in catalogged_object_list:
            #LOG('catalog_object_list: object.uid',0,getattr(object,'uid',None))
            #LOG('catalog_object_list: object.path',0,object.getPhysicalPath())
            try:
              value = getattr(object, arg)
              if callable(value):
                value = value()
              value_list.append(value)
            except:
              #LOG("SQLCatalog Warning: Callable value could not be called",0,str((path, arg, method_name)))
              value_list.append(None)
          kw[arg] = value_list

      method = aq_base(method).__of__(self) # Use method in the context of portal_catalog
      # Alter/Create row
      try:
        #start_time = DateTime()
        method(**kw)
        #end_time = DateTime()
        #if method_name not in profile_dict:
        #  profile_dict[method_name] = end_time.timeTime() - start_time.timeTime()
        #else:
        #  profile_dict[method_name] += end_time.timeTime() - start_time.timeTime()
        #LOG('catalogObjectList', 0, '%s: %f seconds' % (method_name, profile_dict[method_name]))
      except:
        LOG("SQLCatalog Warning: could not catalog objects with method %s" % method_name,100, str(object_list))
        raise

  def uncatalogObject(self, path):
    """
    Uncatalog and object from the Catalog.

    Note, the uid must be the same as when the object was
    catalogued, otherwise it will not get removed from the catalog

    This method should not raise an exception if the uid cannot
    be found in the catalog.

    XXX Add filter of methods

    """
    #LOG('Uncatalog object:',0,str(path))

    uid = self.getUidForPath(path)
    methods = self.sql_uncatalog_object
    for method_name in methods:
      method = getattr(self, method_name)
      try:
        #if 1:
        method(uid = uid)
      except:
        # This is a real LOG message
        # which is required in order to be able to import .zexp files
        LOG("SQLCatalog Warning: could not uncatalog object uid %s with method %s" %
                                               (uid, method_name),0,str(path))

  def uniqueValuesFor(self, name):
    """ return unique values for FieldIndex name """
    method = getattr(self, self.sql_unique_values)
    return method()

  def getPaths(self):
    """ Returns all object paths stored inside catalog """
    method = getattr(self, self.sql_catalog_paths)
    return method()

  def getUidForPath(self, path):
    """ Looks up into catalog table to convert path into uid """
    try:
      if path is None:
        return None
      # Get the appropriate SQL Method
      method = getattr(self, self.sql_getitem_by_path)
      search_result = method(path = path, uid_only=1)
      # If not emptyn return first record
      if len(search_result) > 0:
        return search_result[0].uid
      else:
        return None
    except:
      # This is a real LOG message
      # which is required in order to be able to import .zexp files
      LOG("Warning: could not find uid from path",0,str(path))
      return None

  def hasPath(self, path):
    """ Checks if path is catalogued """
    return self.getUidForPath(path) is not None

  def getPathForUid(self, uid):
    """ Looks up into catalog table to convert uid into path """
    try:
      if uid is None:
        return None
      # Get the appropriate SQL Method
      method = getattr(self, self.sql_getitem_by_uid)
      search_result = method(uid = uid)
      # If not empty return first record
      if len(search_result) > 0:
        return search_result[0].path
      else:
        return None
    except:
      # This is a real LOG message
      # which is required in order to be able to import .zexp files
      LOG("Warning: could not find path from uid",0,str(uid))
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
      if uid is None:
        return None
      # Get the appropriate SQL Method
      method = getattr(self, self.sql_getitem_by_path)
      brain = method(path = path)[0]
      result = {}
      for k in brain.__record_schema__.keys():
        result[k] = getattr(brain,k)
      return result
    except:
      # This is a real LOG message
      # which is required in order to be able to import .zexp files
      LOG("Warning: could not find uid from path",0,str(path))
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
    StringType=type('')

    while self is not None:
      if hasattr(self, 'objectValues'):
        for o in self.objectValues(valid_method_meta_type_list):
          if hasattr(o,'id'):
            id=o.id
            if type(id) is not StringType: id=id()
            if not have_id(id):
              if hasattr(o,'title_and_id'): o=o.title_and_id()
              else: o=id
              ids[id]=id
      if hasattr(self, 'aq_parent'): self=self.aq_parent
      else: self=None

    ids=map(lambda item: (item[1], item[0]), ids.items())
    ids.sort()
    return ids

  def buildSQLQuery(self, query_table='catalog', REQUEST=None, **kw):
    """ Builds a complex SQL query to simulate ZCalatog behaviour """
    # Get search arguments:
    if REQUEST is None and (kw is None or kw == {}):
      # We try to get the REQUEST parameter
      # since we have nothing handy
      try: REQUEST=self.REQUEST
      except AttributeError: pass

    #LOG('SQLCatalog.buildSQLQuery, kw',0,kw)
    # If kw is not set, then use REQUEST instead
    if kw is None or kw == {}:
      kw = REQUEST

    acceptable_key_map = self.getColumnMap()
    acceptable_keys = acceptable_key_map.keys()
    full_text_search_keys = self.sql_catalog_full_text_search_keys
    keyword_search_keys = self.sql_catalog_keyword_search_keys
    topic_search_keys = self.sql_catalog_topic_search_keys
    multivalue_keys = self.sql_catalog_multivalue_keys

    # Define related maps
    # each tuple has the form (key, 'table1,table2,table3/column/where_expression')
    related_tuples = self.sql_catalog_related_keys
    #LOG('related_tuples', 0, str(related_tuples))
    related_keys = []
    related_method = {}
    related_table_map = {}
    related_column = {}
    related_table_map = {}
    table_rename_index = 0
    related_methods = {} # related methods which need to be used
    for t in related_tuples:
      t_tuple = t.split('|')
      key = t_tuple[0].strip()
      join_tuple = t_tuple[1].strip().split('/')
      #LOG('related_tuples', 0, str(join_tuple))
      related_keys.append(key)
      method_id = join_tuple[2]
      related_method[key] = method_id
      related_column[key] = join_tuple[1]
      # Rename tables to prevent conflicts
      if not related_table_map.has_key(method_id):
        map_list = []
        for table_id in join_tuple[0].split(','):
          map_list.append((table_id,
             "related_%s_%s" % (table_id, table_rename_index))) # We add an index in order to alias tables in the join
          table_rename_index += 1 # and prevent name conflicts
        related_table_map[method_id] = map_list

    # We take additional parameters from the REQUEST
    # and give priority to the REQUEST
    if REQUEST is not None:
      for key in acceptable_keys:
        if REQUEST.has_key(key):
          # Only copy a few keys from the REQUEST
          if key in self.sql_catalog_request_keys:
            kw[key] = REQUEST[key]
      # Let us try first not to use this
      #for key in related_keys:
      #  if REQUEST.has_key(key):
      #    kw[key] = REQUEST[key]

    # Let us start building the where_expression
    if kw:
      where_expression = []
      from_table_dict = {'catalog' : 'catalog'} # Always include catalog table


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

      if so is not None:
        if type(so) is type('a'):
          if so.find(',')>0:
            so = [x.strip() for x in so.split(',')]
          else:
            so = [so]

      # We must now turn sort_index into
      # a dict with keys as sort keys and values as sort order
      if type(sort_index) is type('a'):
        sort_index = [(sort_index, so)]
      elif type(sort_index) is not type(()) and type(sort_index) is not type([]):
        sort_index = None
        
      #new_index = []
      #if sort_index is not None:
      #  if type(sort_index) is type('a'):
      #    if sort_index.find(',')>0:
      #      index_list = [x.strip() for x in sort_index.split(',')]
      #    else:
      #      index_list = [sort_index]
      #    for index in index_list:
      #      if index.find(' ') > 0:
      #        new_index.append([x.strip() for x in index.split(' ')])
      #      elif so is not None and len(so)==len(index_list):
      #        new_index.append([index,so[index_list.index(index)]])
      #      else:
      #        new_index.append([index,'ascending'])
      #sort_index = new_index

      # If sort_index is a dictionnary
      # then parse it and change it
      sort_on = None
      #LOG('sorting', 0, str(sort_index))
      if sort_index is not None:
        try:
          new_sort_index = []
          for (k , v) in sort_index:
            if '.' in k:
              pass
            elif len(acceptable_key_map[k]) == 1 :
              k = acceptable_key_map[k][0] + '.' + k
            elif query_table:
              k = query_table + '.' + k
            if v == 'descending' or v == 'reverse' or v == 'DESC':
              from_table_dict[acceptable_key_map[k][0]] = acceptable_key_map[k][0] # We need this table to sort on it
              new_sort_index += ['%s DESC' % k]
            else:
              from_table_dict[acceptable_key_map[k][0]] = acceptable_key_map[k][0] # We need this table to sort on it
              new_sort_index += ['%s' % k]
          sort_index = join(new_sort_index,',')
          sort_on = str(sort_index)
        except:
          LOG('SQLCatalog.buildSQLQuery',0,'WARNING, Unable to build the new sort index')
          pass

      # Rebuild keywords to behave as new style query (_usage='toto:titi' becomes {'toto':'titi'})
      new_kw = {}
      usage_len = len('_usage')
      for k, v in kw.items():
        if k.endswith('_usage'):
          new_k = k[0:-usage_len]
          if not new_kw.has_key(new_k): new_kw[new_k] = {}
          if type(new_kw[new_k]) is not type({}): new_kw[new_k] = {'query': new_kw[new_k]}
          split_v = v.split(':')
          new_kw[new_k] = {split_v[0]: split_v[1]}
        else:
          if not new_kw.has_key(k):
            new_kw[k] = v
          else:
            new_kw[k]['query'] = v
      kw = new_kw
      #LOG('new kw', 0, str(kw))
      # We can now consider that old style query is changed into new style
      for key in kw.keys(): # Do not use kw.items() because this consumes much more memory
        value = kw[key]
        if key not in ('where_expression', 'sort-on', 'sort_on', 'sort-order', 'sort_order'):
          # Make sure key belongs to schema
          key_is_acceptable = key in acceptable_keys # Only calculate once
          key_is_related = key in related_keys
          if key_is_acceptable or key_is_related:
            if key_is_related: # relation system has priority (ex. security_uid)
              # We must rename the key
              method_id = related_method[key]
              if not related_methods.has_key(method_id):
                related_methods[method_id] = 1
              key = "%s.%s" % (related_table_map[method_id][-1][-1], related_column[key]) # Prepend renamed table name
            elif key_is_acceptable:
              if key.find('.') < 0:
                # if the key is only used by one table, just append its name
                if len(acceptable_key_map[key]) == 1 :
                  key = acceptable_key_map[key][0] + '.' + key
                # query_table specifies what table name should be used by default
                elif query_table:
                  key = query_table + '.' + key
                elif key == 'uid':
                  # uid is always ambiguous so we can only change it here
                  key = 'catalog.uid'
              # Add table to table dict
              from_table_dict[acceptable_key_map[key][0]] = acceptable_key_map[key][0] # We use catalog by default
            # Default case: variable equality
            if type(value) is type(''):
              if value != '':
                # we consider empty string as Non Significant
                if value == '=':
                  # But we consider the sign = as empty string
                  value=''
                if '%' in value:
                  where_expression += ["%s LIKE '%s'" % (key, value)]
                elif value[0:2] == '>=':
                  where_expression += ["%s >= '%s'" % (key, value[2:])]
                elif value[0:2] == '<=':
                  where_expression += ["%s <= '%s'" % (key, value[2:])]
                elif value[0] == '>':
                  where_expression += ["%s > '%s'" % (key, value[1:])]
                elif value[0] == '<':
                  where_expression += ["%s < '%s'" % (key, value[1:])]
                elif value[0:2] == '!=':
                  where_expression += ["%s != '%s'" % (key, value[2:])]
                elif key in keyword_search_keys:
                  # We must add % in the request to simulate the catalog
                  where_expression += ["%s LIKE '%%%s%%'" % (key, value)]
                elif key in full_text_search_keys:
                  # We must add % in the request to simulate the catalog
                  where_expression += ["MATCH %s AGAINST ('%s')" % (key, value)]
                else:
                  where_expression += ["%s = '%s'" % (key, value)]
            elif type(value) is type([]) or type(value) is type(()):
              # We have to create an OR from tuple or list
              query_item = []
              for value_item in value:
                if value_item != '':
                  # we consider empty string as Non Significant
                  # also for lists
                  if type(value_item) in (type(1), type(1.0)):
                    query_item += ["%s = %s" % (key, value_item)]
                  else:
                    if '%' in value_item:
                      query_item += ["%s LIKE '%s'" % (key, str(value_item))]
                    elif key in keyword_search_keys:
                      # We must add % in the request to simulate the catalog
                      query_item += ["%s LIKE '%%%s%%'" % (key, str(value_item))]
                    elif key in full_text_search_keys:
                      # We must add % in the request to simulate the catalog
                      query_item +=  ["MATCH %s AGAINST ('%s')" % (key, value)]
                    else:
                      query_item += ["%s = '%s'" % (key, str(value_item))]
              if len(query_item) > 0:
                where_expression += ['(%s)' % join(query_item, ' OR ')]
            elif type(value) is type({}):
              # We are in the case of a complex query
              query_item = []
              query_value = value['query']
              if type(query_value) != type([]) and type(query_value) != type(()) :
                query_value = [query_value]
              operator_value = value.get('operator', 'or')
              range_value = value.get('range')
              
              if range_value :
                query_min = min(query_value)
                query_max = max(query_value)
                if range_value == 'min' :
                  query_item += ["%s >= '%s'" % (key, str(query_min)) ]
                elif range_value == 'max' :
                  query_item += ["%s < '%s'" % (key, str(query_max)) ]
                elif range_value == 'minmax' :
                  query_item += ["%s >= '%s' and %s < '%s'" % (key, str(query_min), key, str(query_max)) ]
                elif range_value == 'ngt' :
                  query_item += ["%s <= '%s'" % (key, str(query_max)) ]
              else :
                for query_value_item in query_value :
                  query_item += ['%s = %s' % (key, str(query_value_item))]
              if len(query_item) > 0:
                where_expression += ['(%s)' % join(query_item, ' %s ' % operator_value)]
            else:
              where_expression += ["%s = %s" % (key, value)]
          elif key in topic_search_keys:
            # ERP5 CPS compatibility
            topic_operator = 'or'
            if type(value) is type({}):
              topic_operator = value.get('operator', 'or')
              value = value['query']
            if type(value) is type(''):
              topic_value = [value]
            else:
              topic_value = value # list or tuple
            query_item = []
            for topic_key in topic_value:
              if topic_key in acceptable_keys:
                if topic_key.find('.') < 0:
                  # if the key is only used by one table, just append its name
                  if len(acceptable_key_map[topic_key]) == 1 :
                    topic_key = acceptable_key_map[topic_key][0] + '.' + topic_key
                  # query_table specifies what table name should be used
                  elif query_table:
                    topic_key = query_table + '.' + topic_key
                # Add table to table dict
                from_table_dict[acceptable_key_map[topic_key][0]] = acceptable_key_map[topic_key][0] # We use catalog by default
                query_item += ["%s = 1" % topic_key]
            # Join
            if len(query_item) > 0:
              where_expression += ['(%s)' % join(query_item, ' %s ' % topic_operator)]
      # Calculate extra where_expression based on required joins
      for k, tid in from_table_dict.items():
        if k != query_table:
          where_expression.append('%s.uid = %s.uid' % (query_table, tid))
      # Calculate extra where_expressions based on related definition
      related_join_expression = []
      for method_id in related_methods.keys():
        related_method = getattr(self, method_id, None)
        if related_method is not None:
          table_id = {'src__' : 1} # Return query source, do not evaluate
          table_index = 0
          for t_tuple in related_table_map[method_id]:
            table_id['table_%s' % table_index] = t_tuple[1] # table_X is set to mapped id
            from_table_dict[t_tuple[1]] = t_tuple[0]
            table_index += 1
          where_expression.append(related_method(**table_id))
      # Concatenate where_expressions
      if kw.get('where_expression'):
        if len(where_expression) > 0:
          where_expression = "(%s) AND (%s)" % (kw['where_expression'], join(where_expression, ' AND ') )
      else:
        where_expression = join(where_expression, ' AND ')

    # Use a dictionary at the moment.
    return { 'from_table_list' : from_table_dict.items(),
             'order_by_expression' : sort_on,
             'where_expression' : where_expression }

  def queryResults(self, sql_method, REQUEST=None, used=None, src__=0, **kw):
    """ Returns a list of brains from a set of constraints on variables """
    query = self.buildSQLQuery(REQUEST=REQUEST, **kw)
    kw['where_expression'] = query['where_expression']
    kw['sort_on'] = query['order_by_expression']
    kw['from_table_list'] = query['from_table_list']
    # Return the result

    #LOG('acceptable_keys',0,'acceptable_keys: %s' % str(acceptable_keys))
    #LOG('acceptable_key_map',0,'acceptable_key_map: %s' % str(acceptable_key_map))
    #LOG('queryResults',0,'kw: %s' % str(kw))
    #LOG('queryResults',0,'from_table_list: %s' % str(from_table_dict.keys()))
    return sql_method(src__=src__, **kw)

  def searchResults(self, REQUEST=None, used=None, **kw):
    """ Builds a complex SQL where_expression to simulate ZCalatog behaviour """
    """ Returns a list of brains from a set of constraints on variables """
    # The used argument is deprecated and is ignored      
    try:
      # Get the search method
      method = getattr(self, self.sql_search_results)
      # Return the result
      kw['used'] = used
      kw['REQUEST'] = REQUEST
      return self.queryResults(method, **kw)
    except:
      LOG("Warning: could not search catalog",0,self.sql_search_results, error=sys.exc_info())
      return []

  __call__ = searchResults

  def countResults(self, REQUEST=None, used=None, **kw):
    """ Builds a complex SQL where_expression to simulate ZCalatog behaviour """
    """ Returns the number of items which satisfy the where_expression """
    try:
      # Get the search method
      method = getattr(self, self.sql_count_results)
      # Return the result
      kw['used'] = used
      kw['REQUEST'] = REQUEST
      return self.queryResults(method, **kw)
    except:
      LOG("Warning: could not count catalog",0,self.sql_count_results, error=sys.exc_info())
      return [[0]]

  def recordCatalogObject(self, path):
    """
      Record the path of an object being catalogged.
    """
    method = getattr(self, self.sql_record_catalog_object)
    method(path=path)

  def recordUncatalogObject(self, path):
    """
      Record the path of an object being uncatalogged.
    """
    method = getattr(self, self.sql_record_uncatalog_object)
    method(path=path)

  def deleteRecordedObjectList(self, path):
    """
      Delete all objects which contain any path.
    """
    if type(path) == type(''):
      path = [path]
    method = getattr(self, self.sql_delete_recorded_object_list)
    method(path=path)

  def readRecordedObjectList(self):
    """
      Read objects. Note that this might not return all objects since ZMySQLDA limits the max rows.
    """
    method = getattr(self, self.sql_read_recorded_object_list)
    return method()

  # Filtering
  def manage_editFilter(self, REQUEST=None, RESPONSE=None, URL1=None):
    """
    This methods allows to set a filter on each zsql method called,
    so we can test if we should or not call a zsql method, so we can
    increase a lot the speed.
    """
    if withCMF:
      for zsql_method in self.getFilterableMethodList():
        # We will first look if the filter is activated
        id = zsql_method.id
        if not self.filter_dict.has_key(id):
          self.filter_dict[id] = PersistentMapping()
          self.filter_dict[id]['filtered']=0
          self.filter_dict[id]['type']=[]
          self.filter_dict[id]['expression']=""
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
          if type(list_type) is type('a'):
            list_type = [list_type]
          self.filter_dict[id]['type'] = list_type
        else:
          self.filter_dict[id]['type'] = []

    if RESPONSE and URL1:
      RESPONSE.redirect(URL1 + '/manage_catalogFilter?manage_tabs_message=Filter%20Changed')

  def isMethodFiltered(self, method_name):
    """
    Returns 1 if the method is already filtered,
    else it returns 0
    """
    if withCMF:
      # Reset Filtet dict
      # self.filter_dict= PersistentMapping()
      if not hasattr(self,'filter_dict'):
        self.filter_dict = PersistentMapping()
        return 0
      if self.filter_dict.has_key(method_name):
        return self.filter_dict[method_name]['filtered']
    return 0

  def getExpression(self, method_name):
    """
    Returns 1 if the method is already filtered,
    else it returns 0
    """
    if withCMF:
      if not hasattr(self,'filter_dict'):
        self.filter_dict = PersistentMapping()
        return ""
      if self.filter_dict.has_key(method_name):
        return self.filter_dict[method_name]['expression']
    return ""

  def getExpressionInstance(self, method_name):
    """
    Returns 1 if the method is already filtered,
    else it returns 0
    """
    if withCMF:
      if not hasattr(self,'filter_dict'):
        self.filter_dict = PersistentMapping()
        return None
      if self.filter_dict.has_key(method_name):
        return self.filter_dict[method_name]['expression_instance']
    return None

  def isPortalTypeSelected(self, method_name,portal_type):
    """
    Returns 1 if the method is already filtered,
    else it returns 0
    """
    if withCMF:
      if not hasattr(self,'filter_dict'):
        self.filter_dict = PersistentMapping()
        return 0
      if self.filter_dict.has_key(method_name):
        result = portal_type in (self.filter_dict[method_name]['type'])
        return result
    return 0


  def getFilterableMethodList(self):
    """
    Returns only zsql methods wich catalog or uncatalog objets
    """
    method_dict = {}
    if withCMF:
      methods = self.sql_catalog_object + self.sql_uncatalog_object \
                + self.sql_update_object + self.sql_catalog_object_list
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
            'root':         ob.getPhysicalRoot(),
            'request':      getattr( ob, 'REQUEST', None ),
            'modules':      SecureModuleImporter,
            'user':         getSecurityManager().getUser(),
            }
        return getEngine().getContext(data)


Globals.default__class_init__(Catalog)

class CatalogError(Exception): pass
