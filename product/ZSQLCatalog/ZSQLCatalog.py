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
"""ZCatalog product"""

from Globals import DTMLFile, MessageDialog
import Globals

from OFS.Folder import Folder
from OFS.FindSupport import FindSupport
from OFS.ObjectManager import ObjectManager
from DateTime import DateTime
from Acquisition import Implicit
from Persistence import Persistent
from DocumentTemplate.DT_Util import InstanceDict, TemplateDict
from DocumentTemplate.DT_Util import Eval
from AccessControl.Permission import name_trans
from SQLCatalog import Catalog, CatalogError
from AccessControl import getSecurityManager
from AccessControl.DTML import RestrictedDTML
import string, urllib, os, sys, time, types

from zLOG import LOG

valid_method_meta_type_list = ('Z SQL Method','Script (Python)')

manage_addZCatalogForm=DTMLFile('dtml/addZCatalog',globals())

def manage_addZCatalog(self, id, title,
             vocab_id='create_default_catalog_',
             REQUEST=None):
  """Add a ZCatalog object
  """
  id=str(id)
  title=str(title)
  vocab_id=str(vocab_id)
  if vocab_id == 'create_default_catalog_':
    vocab_id = None

  c=ZCatalog(id, title, self)
  self._setObject(id, c)
  if REQUEST is not None:
    return self.manage_main(self, REQUEST,update_menu=1)


class ZCatalog(Folder, Persistent, Implicit):
  """ZCatalog object

  A ZCatalog contains arbirary index like references to Zope
  objects.  ZCatalog's can index either 'Field' values of object, or
  'Text' values.

  ZCatalog does not store references to the objects themselves, but
  rather to a unique identifier that defines how to get to the
  object.  In Zope, this unique idenfier is the object's relative
  path to the ZCatalog (since two Zope object's cannot have the same
  URL, this is an excellent unique qualifier in Zope).

  Most of the dirty work is done in the _catalog object, which is an
  instance of the Catalog class.  An interesting feature of this
  class is that it is not Zope specific.  You can use it in any
  Python program to catalog objects.

  """

  meta_type = "ZSQLCatalog"
  icon='misc_/ZCatalog/ZCatalog.gif'

  manage_options = (
    {'label': 'Contents',       # TAB: Contents
     'action': 'manage_main',
     'help': ('OFSP','ObjectManager_Contents.stx')},
    {'label': 'Catalog',      # TAB: Cataloged Objects
     'action': 'manage_catalogView',
     'target': 'manage_main',
     'help':('ZCatalog','ZCatalog_Cataloged-Objects.stx')},
    {'label': 'Properties',     # TAB: Properties
     'action': 'manage_propertiesForm',
     'help': ('OFSP','Properties.stx')},
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
      'catalog_object', 'uncatalog_object', 'refreshCatalog',

      'manage_catalogView', 'manage_catalogFind',
      'manage_catalogSchema',
      'manage_catalogAdvanced', 'manage_objectInformation',

      'manage_catalogReindex', 'manage_catalogFoundItems',
      'manage_catalogClear', 'manage_editSchema',
      'manage_reindexIndex', 'manage_main',

      ],
     ['Manager']),

    ('Search ZCatalog',
     ['searchResults', '__call__', 'uniqueValuesFor',
      'getpath', 'schema', 'names', 'columns', 'indexes', 'index_objects',
      'all_meta_types', 'valid_roles', 'resolve_url',
      'getobject', 'getObject', 'getObjectList', 'getCatalogSearchTableIds',
      'getCatalogSearchResultKeys', ],
     ['Anonymous', 'Manager']),
    )

  _properties = (
    { 'id'      : 'title',
      'description' : 'The title of this catalog',
      'type'    : 'string',
      'mode'    : 'w' },
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
  )

  sql_catalog_produce_reserved = 'z_produce_reserved_uid_list'
  sql_catalog_clear_reserved = 'z_clear_reserved'
  sql_catalog_object = ('catalog_object',)
  sql_uncatalog_object = ('uncatalog_object',)
  sql_update_object = ('update_object',)
  sql_clear_catalog = ('drop_catalog', 'create_catalog')
  sql_search_results = 'search_results'
  sql_count_results = 'count_results'
  sql_getitem_by_path = 'getitem_by_path'
  sql_getitem_by_uid = 'getitem_by_uid'
  sql_catalog_tables = 'catalog_tables'
  sql_search_tables = ()
  sql_catalog_schema = ('catalog_schema')
  sql_unique_values = 'unique_values'
  sql_catalog_paths = 'catalog_paths'
  sql_catalog_keyword_search_keys =  ('Description', 'Title', 'SearchableText')
  sql_catalog_full_text_search_keys = ()
  sql_catalog_request_keys = ()
  sql_search_result_keys = ()


  manage_catalogAddRowForm = DTMLFile('dtml/catalogAddRowForm', globals())
  manage_catalogView = DTMLFile('dtml/catalogView',globals())
  manage_catalogFind = DTMLFile('dtml/catalogFind',globals())
  manage_catalogSchema = DTMLFile('dtml/catalogSchema', globals())
  manage_catalogIndexes = DTMLFile('dtml/catalogIndexes', globals())
  manage_catalogAdvanced = DTMLFile('dtml/catalogAdvanced', globals())
  manage_objectInformation = DTMLFile('dtml/catalogObjectInformation',
                                                              globals())

  def __init__(self, id, title='', container=None):
    if container is not None:
      self=self.__of__(container)
    self.id=id
    self.title=title
    self._catalog = Catalog()
    """
    self.addColumn('id')
    self.addIndex('id', 'FieldIndex')

    self.addColumn('title')
    self.addIndex('title', 'TextIndex')

    self.addColumn('meta_type')
    self.addIndex('meta_type', 'FieldIndex')

    self.addColumn('bobobase_modification_time')
    self.addIndex('bobobase_modification_time', 'FieldIndex')

    self.addColumn('summary')
    self.addIndex('PrincipiaSearchSource', 'TextIndex')

    self.addIndex('path','PathIndex')
    """

  def __len__(self): return len(self._catalog)

  def manage_edit(self, RESPONSE, URL1, threshold=1000, REQUEST=None):
    """ edit the catalog """
    if type(threshold) is not type(1):
      threshold=string.atoi(threshold)
    self.threshold = threshold

    RESPONSE.redirect(URL1 + '/manage_main?manage_tabs_message=Catalog%20Changed')


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
          self.catalog_object(obj, url)

    RESPONSE.redirect(URL1 + '/manage_catalogView?manage_tabs_message=Object%20Cataloged')


  def manage_uncatalogObject(self, REQUEST, RESPONSE, URL1, urls=None):
    """ removes Zope object(s) 'urls' from catalog """

    if urls:
      if isinstance(urls, types.StringType):
        urls=(urls,)

      for url in urls:
        self.uncatalog_object(url)

    RESPONSE.redirect(URL1 + '/manage_catalogView?manage_tabs_message=Object%20Uncataloged')


  def manage_catalogReindex(self, REQUEST, RESPONSE, URL1):
    """ clear the catalog, then re-index everything """
    elapse = time.time()
    c_elapse = time.clock()

    self.refreshCatalog(clear=1)

    elapse = time.time() - elapse
    c_elapse = time.clock() - c_elapse

    RESPONSE.redirect(URL1 +
              '/manage_catalogAdvanced?manage_tabs_message=' +
              urllib.quote('Catalog Updated<br>'
                     'Total time: %s<br>'
                     'Total CPU time: %s' % (`elapse`, `c_elapse`)))


  def refreshCatalog(self, clear=0):
    """ re-index everything we can find """

    cat = self._catalog
    paths = cat.getPaths()
    if clear:
      cat.clear()

    for p in paths:
      obj = self.resolve_path(p.path)
      if not obj:
        obj = self.resolve_url(p.path, self.REQUEST)
      if obj is not None:
        self.catalog_object(obj, p.path)

  def manage_catalogClear(self, REQUEST=None, RESPONSE=None, URL1=None):
    """ clears the whole enchilada """
    self._catalog.clear()

    if REQUEST and RESPONSE:
      RESPONSE.redirect(URL1 + '/manage_catalogAdvanced?manage_tabs_message=Catalog%20Cleared')


  def manage_catalogClearReserved(self, REQUEST=None, RESPONSE=None, URL1=None):
    """ clears the whole enchilada """
    self._catalog.clearReserved()

    if REQUEST and RESPONSE:
      RESPONSE.redirect(URL1 + '/manage_catalogAdvanced?manage_tabs_message=Catalog%20Cleared')

  
  def manage_catalogCreateTables(self, REQUEST=None, RESPONSE=None, URL1=None):
    """ creates the tables required for cataging objects """
    self._catalog.createTables()

    if REQUEST and RESPONSE:
      RESPONSE.redirect(URL1 + '/manage_catalogAdvanced?manage_tabs_message=Tables%20Created')


  def manage_catalogDropTables(self, REQUEST=None, RESPONSE=None, URL1=None):
    """ drops the tables required for cataging objects """
    self._catalog.dropTables()

    if REQUEST and RESPONSE:
      RESPONSE.redirect(URL1 + '/manage_catalogAdvanced?manage_tabs_message=Tables%20Dropped')

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


    results = self.ZopeFindAndApply(obj,
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
                    apply_func=self.catalog_object,
                    apply_path=path)

    elapse = time.time() - elapse
    c_elapse = time.clock() - c_elapse

    RESPONSE.redirect(URL1 + '/manage_catalogView?manage_tabs_message=' +
              urllib.quote('Catalog Updated<br>Total time: %s<br>Total CPU time: %s' % (`elapse`, `c_elapse`)))


  def manage_editSchema(self, names, REQUEST=None, RESPONSE=None, URL1=None):
    """ add a column """
    self.editSchema(names)

    if REQUEST and RESPONSE:
      RESPONSE.redirect(URL1 + '/manage_catalogSchema?manage_tabs_message=Schema%20Saved')

  def newUid(self):
    """
        Allocates a new uid value.
    """
    return self._catalog.newUid()
      
  def catalog_object(self, obj, uid=None, idxs=[], is_object_moved=0):
    """ wrapper around catalog """

    if uid is None:
      try: uid = obj.getPhysicalPath
      except AttributeError:
        raise CatalogError(
          "A cataloged object must support the 'getPhysicalPath' "
          "method if no unique id is provided when cataloging"
          )
      else: uid=string.join(uid(), '/')
    elif not isinstance(uid, types.StringType):
      raise CatalogError('The object unique id must be a string.')

    self._catalog.catalogObject(obj, uid, is_object_moved=is_object_moved)

  def uncatalog_object(self, uid):
    """ wrapper around catalog """
    self._catalog.uncatalogObject(uid)

  def uniqueValuesFor(self, name):
    """ returns the unique values for a given FieldIndex """
    return self._catalog.uniqueValuesFor(name)

  def getpath(self, uid):
    """
    Return the path to a cataloged object given its uid
    """
    object = self._catalog[uid]
    if object:
      return object.path
    else:
      return None
  getPath = getpath

  def getobject(self, uid, REQUEST=None):
    """
    Return a cataloged object given its uid
    """
    try:
      obj = self.aq_parent.unrestrictedTraverse(self.getpath(uid))
    except:
      LOG('WARNING: ZSQLCatalog',0,'Could not find object for uid %s' % uid)
      obj = None
    if obj is not None:
      if REQUEST is None:
        REQUEST=self.REQUEST
      path = self.getpath(uid)
      if path:
        obj = self.resolve_url(path, REQUEST)
      else:
        obj = None
    return obj
  getObject = getobject

  def getObjectList(self, uid_list, REQUEST=None):
    """
    Return a cataloged object given its uid
    """
    obj_list = []
    for uid in uid_list:
      obj_list.append(self.getObject(uid, REQUEST))
    return obj_list

  def getMetadataForUid(self, rid):
    """return the correct metadata for the cataloged uid"""
    return self._catalog.getMetadataForUid(int(rid))

  def getIndexDataForUid(self, rid):
    """return the current index contents for the specific uid"""
    return self._catalog.getIndexDataForUid(rid)

  # Aliases
  getMetadataForRID = getMetadataForUid
  getIndexDataForRID = getIndexDataForUid

  def schema(self):
    return self.getColumnIds()

  def indexes(self):
    return self.getColumnIds()

  def names(self):
    return self._catalog.names

  def getColumnIds(self):
    return self._catalog.getColumnIds()

  def getAttributesForColumn(self, column):
    """
      Return the attribute names as a single string
    """
    return string.join(self.names().get(column, ('',)),' ')

  def _searchable_arguments(self):
    return self._catalog.getColumnIds()

  def editSchema(self,names):
    self._catalog.editSchema(names)

  def _searchable_result_columns(self):
    r = []
    for name in self._catalog.getColumnIds():
      i = {}
      i['name'] = name
      i['type'] = 's'
      i['parser'] = str
      i['width'] = 8
      r.append(i)
    r.append({'name': 'data_record_id_',
          'type': 's',
          'parser': str,
          'width': 8})
    return r

  def getColumnIds(self):
    return self._catalog.getColumnIds()

  def searchResults(self, REQUEST=None, used=None, **kw):
    """
    Search the catalog according to the ZTables search interface.
    Search terms can be passed in the REQUEST or as keyword
    arguments.
    """
    return apply(self._catalog.searchResults, (REQUEST,used), kw)

  __call__=searchResults

  def countResults(self, REQUEST=None, used=None, **kw):
    """
    Counts the number of items which satisfy the query defined in kw.
    """
    return apply(self._catalog.countResults, (REQUEST,used), kw)

## this stuff is so the find machinery works

  meta_types=() # Sub-object types that are specific to this object

  def valid_roles(self):
    "Return list of valid roles"
    obj=self
    dict={}
    dup =dict.has_key
    x=0
    while x < 100:
      if hasattr(obj, '__ac_roles__'):
        roles=obj.__ac_roles__
        for role in roles:
          if not dup(role):
            dict[role]=1
      if not hasattr(obj, 'aq_parent'):
        break
      obj=obj.aq_parent
      x=x+1
    roles=dict.keys()
    roles.sort()
    return roles

  def ZopeFindAndApply(self, obj, obj_ids=None, obj_metatypes=None,
             obj_searchterm=None, obj_expr=None,
             obj_mtime=None, obj_mspec=None,
             obj_permission=None, obj_roles=None,
             search_sub=0,
             REQUEST=None, result=None, pre='',
             apply_func=None, apply_path=''):
    """Zope Find interface and apply

    This is a *great* hack.  Zope find just doesn't do what we
    need here; the ability to apply a method to all the objects
    *as they're found* and the need to pass the object's path into
    that method.

    """

    if result is None:
      result=[]

      if obj_metatypes and 'all' in obj_metatypes:
        obj_metatypes=None

      if obj_mtime and type(obj_mtime)==type('s'):
        obj_mtime=DateTime(obj_mtime).timeTime()

      if obj_permission:
        obj_permission=p_name(obj_permission)

      if obj_roles and type(obj_roles) is type('s'):
        obj_roles=[obj_roles]

      if obj_expr:
        # Setup expr machinations
        md=td()
        obj_expr=(Eval(obj_expr), md, md._push, md._pop)

    base=obj
    if hasattr(obj, 'aq_base'):
      base=obj.aq_base

    if not hasattr(base, 'objectItems'):
      return result
    try:  items=obj.objectItems()
    except: return result

    try: add_result=result.append
    except:
      raise AttributeError, `result`

    for id, ob in items:
      if pre: p="%s/%s" % (pre, id)
      else:   p=id

      dflag=0
      if hasattr(ob, '_p_changed') and (ob._p_changed == None):
        dflag=1

      if hasattr(ob, 'aq_base'):
        bs=ob.aq_base
      else: bs=ob

      if (
        (not obj_ids or absattr(bs.id) in obj_ids)
        and
        (not obj_metatypes or (hasattr(bs, 'meta_type') and
         bs.meta_type in obj_metatypes))
        and
        (not obj_searchterm or
         (hasattr(ob, 'PrincipiaSearchSource') and
          string.find(ob.PrincipiaSearchSource(), obj_searchterm) >= 0
          ))
        and
        (not obj_expr or expr_match(ob, obj_expr))
        and
        (not obj_mtime or mtime_match(ob, obj_mtime, obj_mspec))
        and
        ( (not obj_permission or not obj_roles) or \
           role_match(ob, obj_permission, obj_roles)
        )
        ):
        if apply_func:
          apply_func(ob, (apply_path+'/'+p))
        else:
          add_result((p, ob))
          dflag=0

      if search_sub and hasattr(bs, 'objectItems'):
        self.ZopeFindAndApply(ob, obj_ids, obj_metatypes,
                    obj_searchterm, obj_expr,
                    obj_mtime, obj_mspec,
                    obj_permission, obj_roles,
                    search_sub,
                    REQUEST, result, p,
                    apply_func, apply_path)
      if dflag: ob._p_deactivate()

    return result

  def resolve_url(self, path, REQUEST):
    """
    Attempt to resolve a url into an object in the Zope
    namespace. The url may be absolute or a catalog path
    style url. If no object is found, None is returned.
    No exceptions are raised.
    """
    script=REQUEST.script
    if string.find(path, script) != 0:
      path='%s/%s' % (script, path)
    try: return REQUEST.resolve_url(path)
    except: pass

  def resolve_path(self, path):
    """
    Attempt to resolve a url into an object in the Zope
    namespace. The url may be absolute or a catalog path
    style url. If no object is found, None is returned.
    No exceptions are raised.
    """
    try: return self.unrestrictedTraverse(path)
    except: pass

  def manage_normalize_paths(self, REQUEST):
    """Ensure that all catalog paths are full physical paths

    This should only be used with ZCatalogs in which all paths can
    be resolved with unrestrictedTraverse."""

    paths = self._catalog.paths
    uids = self._catalog.uids
    unchanged = 0
    fixed = []
    removed = []

    for path, rid in uids.items():
      ob = None
      if path[:1] == '/':
        ob = self.resolve_url(path[1:],REQUEST)
      if ob is None:
        ob = self.resolve_url(path, REQUEST)
        if ob is None:
          removed.append(path)
          continue
      ppath = string.join(ob.getPhysicalPath(), '/')
      if path != ppath:
        fixed.append((path, ppath))
      else:
        unchanged = unchanged + 1

    for path, ppath in fixed:
      rid = uids[path]
      del uids[path]
      paths[rid] = ppath
      uids[ppath] = rid
    for path in removed:
      self.uncatalog_object(path)

    return MessageDialog(title='Done Normalizing Paths',
      message='%s paths normalized, %s paths removed, and '
          '%s unchanged.' % (len(fixed), len(removed), unchanged),
      action='./manage_main')

  def getTableIds(self):
    """Returns all tables of this catalog
    """
    return self._catalog.getTableIds()

  def getCatalogSearchResultKeys(self):
    """Return selected tables of catalog which are used in JOIN.
       catalaog is always first
    """
    return self.sql_search_result_keys

  def getCatalogSearchTableIds(self):
    """Return selected tables of catalog which are used in JOIN.
       catalaog is always first
    """
    if len(self.sql_search_tables) > 0:
      if self.sql_search_tables[0] != 'catalog':
        result = ['catalog']
        for t in self.sql_search_tables:
          if t != 'catalog':
            result.append(t)
        self.sql_search_tables = result
    else:
      self.sql_search_tables = ['catalog']
    return self.sql_search_tables

  def getResultColumnIds(self):
    """Return selected tables of catalog which are used
       as metadata
    """
    return self._catalog.getResultColumnIds()

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


Globals.default__class_init__(ZCatalog)


def p_name(name):
  return '_' + string.translate(name, name_trans) + '_Permission'

def absattr(attr):
  if callable(attr): return attr()
  return attr


class td(RestrictedDTML, TemplateDict):
  pass

def expr_match(ob, ed, c=InstanceDict, r=0):
  e, md, push, pop=ed
  push(c(ob, md))
  try: r=e.eval(md)
  finally:
    pop()
    return r

def mtime_match(ob, t, q, fn=hasattr):
  if not fn(ob, '_p_mtime'):
    return 0
  return q=='<' and (ob._p_mtime < t) or (ob._p_mtime > t)

def role_match(ob, permission, roles, lt=type([]), tt=type(())):
  pr=[]
  fn=pr.append
  
  while 1:
    if hasattr(ob, permission):
      p=getattr(ob, permission)
      if type(p) is lt:
        map(fn, p)
        if hasattr(ob, 'aq_parent'):
          ob=ob.aq_parent
          continue
        break
      if type(p) is tt:
        map(fn, p)
        break
      if p is None:
        map(fn, ('Manager', 'Anonymous'))
        break

    if hasattr(ob, 'aq_parent'):
      ob=ob.aq_parent
      continue
    break

  for role in roles:
    if not (role in pr):
      return 0
  return 1
