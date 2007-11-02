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
from Acquisition import Implicit, aq_base
from Persistence import Persistent
from DocumentTemplate.DT_Util import InstanceDict, TemplateDict
from DocumentTemplate.DT_Util import Eval
from AccessControl.Permission import name_trans
from SQLCatalog import Catalog, CatalogError
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.DTML import RestrictedDTML
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Cache import clearCache
import string, os, sys, types
import time
import urllib
from ZODB.POSException import ConflictError

from zLOG import LOG, ERROR, INFO

_marker = object()

manage_addZSQLCatalogForm=DTMLFile('dtml/addZSQLCatalog',globals())

HOT_REINDEXING_FINISHED_STATE = 'finished'
HOT_REINDEXING_RECORDING_STATE = 'recording'
HOT_REINDEXING_DOUBLE_INDEXING_STATE = 'double indexing'

def manage_addZSQLCatalog(self, id, title,
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
  security = ClassSecurityInfo()

  manage_options = (
    {'label': 'Contents',       # TAB: Contents
     'action': 'manage_main',
     'help': ('OFSP','ObjectManager_Contents.stx')},
    {'label': 'Catalog',      # TAB: Cataloged Objects
     'action': 'manage_catalogView',
     'help':('ZCatalog','ZCatalog_Cataloged-Objects.stx')},
    {'label' : 'Filter',        # TAB: Filter
     'action' : 'manage_catalogFilter' },
    {'label': 'Properties',     # TAB: Properties
     'action': 'manage_propertiesForm',
     'help': ('OFSP','Properties.stx')},
    {'label': 'Find Objects',     # TAB: Find Objects
     'action': 'manage_catalogFind',
     'help':('ZCatalog','ZCatalog_Find-Items-to-ZCatalog.stx')},
    {'label': 'Advanced',       # TAB: Advanced
     'action': 'manage_catalogAdvanced',
     'help':('ZCatalog','ZCatalog_Advanced.stx')},
    {'label': 'Hot Reindexing',       # TAB: Hot Reindex
     'action': 'manage_catalogHotReindexing',
     },
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
      'manage_catalogSchema', 'manage_catalogFilter',
      'manage_catalogAdvanced', 'manage_objectInformation',
      'manage_catalogHotReindexing',

      'manage_catalogReindex', 'manage_catalogFoundItems',
      'manage_catalogClear', 'manage_editSchema',
      'manage_main',
      'manage_editFilter',

      'manage_hotReindexAll',

      ],
     ['Manager']),

    ('Search ZCatalog',
     ['searchResults', '__call__', 'uniqueValuesFor',
      'getpath', 'schema', 'names', 'indexes',
      'all_meta_types', 'valid_roles', 'resolve_url',
      'getobject', 'getObject', 'getObjectList', 'getCatalogSearchTableIds',
      'getCatalogSearchResultKeys', 'getFilterableMethodList', ],
     ['Anonymous', 'Manager']),

    ('Import/Export objects',
     ['manage_catalogExportProperties', 'manage_catalogImportProperties', ],
     ['Manager']),

    )

  _properties = (
    { 'id'      : 'title',
      'description' : 'The title of this catalog',
      'type'    : 'string',
      'mode'    : 'w' },
    { 'id'      : 'default_sql_catalog_id',
      'description' : 'The id of the default SQL Catalog',
      'type'    : 'selection',
      'select_variable'    : 'getSQLCatalogIdList',
      'mode'    : 'w' },

    # Hot Reindexing
    { 'id'      : 'source_sql_catalog_id',
      'description' : 'The id of a source SQL Catalog for hot reindexing',
      'type'    : 'string',
      'mode'    : '' },
    { 'id'      : 'destination_sql_catalog_id',
      'description' : 'The id of a destination SQL Catalog for hot reindexing',
      'type'    : 'string',
      'mode'    : '' },
    { 'id'      : 'hot_reindexing_state',
      'description' : 'The state of hot reindexing',
      'type'    : 'string',
      'mode'    : '' },

  )

  source_sql_catalog_id = None
  destination_sql_catalog_id = None
  hot_reindexing_state = None
  default_sql_catalog_id = None
  archive_path = None
  
  manage_catalogAddRowForm = DTMLFile('dtml/catalogAddRowForm', globals())
  manage_catalogFilter = DTMLFile( 'dtml/catalogFilter', globals() )
  manage_catalogView = DTMLFile('dtml/catalogView',globals())
  manage_catalogFind = DTMLFile('dtml/catalogFind',globals())
  manage_catalogSchema = DTMLFile('dtml/catalogSchema', globals())
  manage_catalogIndexes = DTMLFile('dtml/catalogIndexes', globals())
  manage_catalogAdvanced = DTMLFile('dtml/catalogAdvanced', globals())
  manage_catalogHotReindexing = DTMLFile('dtml/catalogHotReindexing', globals())
  manage_objectInformation = DTMLFile('dtml/catalogObjectInformation',
                                                              globals())

  def __init__(self, id, title='', container=None):
    if container is not None:
      self=self.__of__(container)
    self.id=id
    self.title=title

  def getSQLCatalogIdList(self):
    return self.objectIds(spec=('SQLCatalog',))

  def getSQLCatalog(self, id=None, default_value=None):
    """
      Get the default SQL Catalog.
    """
    if id is None:
      if not self.default_sql_catalog_id:
        id_list = self.getSQLCatalogIdList()
        if len(id_list) > 0:
          self.default_sql_catalog_id = id_list[0]
        else:
          return default_value
      id = self.default_sql_catalog_id

    return self._getOb(id, default_value)

  def manage_catalogExportProperties(self, REQUEST=None, RESPONSE=None, sql_catalog_id=None):
    """
      Export properties to an XML file.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.manage_exportProperties(REQUEST=REQUEST, RESPONSE=RESPONSE)

  def manage_catalogImportProperties(self, file, sql_catalog_id=None):
    """
      Import properties from an XML file.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.manage_importProperties(file)

  def __len__(self):
    catalog = self.getSQLCatalog()
    if catalog is None:
      return 0
    return len(catalog)

  def getHotReindexingState(self):
    """
      Return the current hot reindexing state.
    """
    value = getattr(self, 'hot_reindexing_state', None)
    if value is None:
      return HOT_REINDEXING_FINISHED_STATE
    return value

  def setHotReindexingState(self, state='', source_sql_catalog_id=None, destination_sql_catalog_id=None, archive_path=None):
    """
      Set the state of hot reindexing.

      Do not use setProperty because the state should not modified from the ZMI directly.
      It must be maintained very carefully.
    """
    #LOG("setHotReindexingState call", 300, state)
    if source_sql_catalog_id is None:
      source_sql_catalog_id = self.default_sql_catalog_id

    if state == HOT_REINDEXING_FINISHED_STATE:
      self.hot_reindexing_state = None
      self.source_sql_catalog_id = None
      self.destination_sql_catalog_id = None
      self.archive_path = None
    elif state == HOT_REINDEXING_RECORDING_STATE or \
         state == HOT_REINDEXING_DOUBLE_INDEXING_STATE:
      self.hot_reindexing_state = state
      self.source_sql_catalog_id = source_sql_catalog_id
      self.destination_sql_catalog_id = destination_sql_catalog_id
      self.archive_path = archive_path
    else:
      raise CatalogError, 'unknown hot reindexing state %s' % state

  def finishHotReindexing(self, source_sql_catalog_id,
                          destination_sql_catalog_id, skin_selection_dict,
                          sql_connection_id_dict):
    """
      Exchange databases and finish reindexing in the same transaction.
    """
    self.exchangeDatabases(source_sql_catalog_id=source_sql_catalog_id,
                           destination_sql_catalog_id=destination_sql_catalog_id,
                           skin_selection_dict=skin_selection_dict,
                           sql_connection_id_dict=sql_connection_id_dict)
    self.setHotReindexingState(state=HOT_REINDEXING_FINISHED_STATE)
    clearCache(cache_factory_list=('erp5_content_short',))

  def cancelHotReindexing(self):
    """
      Cancel a hot reindexing.
      Remove the hot reindexing state and flush related activities.

      TODO: Find a safe way to remove activities started by
            ERP5Site_reindexAll.
    """
    if self.getHotReindexingState() == HOT_REINDEXING_FINISHED_STATE:
      raise Exception, 'cancelHotReindexing called while no Hot Reindexing '\
                       'was runing. Nothing done.'
    # Remove hot reindexing state
    self.setHotReindexingState(HOT_REINDEXING_FINISHED_STATE)
    portal_activities = getToolByName(self, 'portal_activities')
    if portal_activities is not None:
      object_path = self.getPhysicalPath()
      # Activities must be removed in the reverse order they were inserted
      # to make sure removing one does not accidntaly trigger the next one.
      method_id_list = ('finishHotReindexing', 'playBackRecordedObjectList',
                        'setHotReindexingState')
      for method_id in method_id_list:
        portal_activities.flush(object_path, method_id=method_id)

  def playBackRecordedObjectList(self, sql_catalog_id, catalog=0):
    """
      Play back the actions scheduled while hot reindexing was in "record"
      state.

      sql_catalog_id   Id of the catalog on which the actions will be played.
      catalog          0 : play unindex actions
                       1 : play index actions

      This function schedules itself for later execution.
      This is done in order to avoid accessing "too many" objects in the same
      transaction.
    """
    if self.getHotReindexingState() != HOT_REINDEXING_DOUBLE_INDEXING_STATE:
      raise Exception, 'playBackRecordedObjectList was called while '\
                       'hot_reindexing_state was not "%s". Playback aborted.' \
                       % (HOT_REINDEXING_DOUBLE_INDEXING_STATE, )
    catalog_object = self.getSQLCatalog(sql_catalog_id)
    result = catalog_object.readRecordedObjectList(catalog=catalog)
    if len(result):
      for o in result:
        if catalog==0:
          self.uncatalog_object(uid=o.path, sql_catalog_id=sql_catalog_id)
        elif catalog==1:
          try:
            obj = self.resolve_path(o.path)
          except ConflictError:
            raise
          except:
            obj = None
          if obj is not None:
            obj.reindexObject(sql_catalog_id=sql_catalog_id)
        else:
          raise ValueError, '%s is not a valid value for "catalog".' % (catalog, )
      catalog_object.deleteRecordedObjectList(uid_list=[o.uid for o in result])
      # Re-schedule the same action in case there are remaining rows in the
      # table. This can happen if the database connector limits the number
      # of rows in the result.
      self.activate(passive_commit=1, priority=5).\
          playBackRecordedObjectList(sql_catalog_id=sql_catalog_id,
                                     catalog=catalog)
    else:
      # If there iss nothing to do, go to next step.
      if catalog == 0:
        # If we were replaying unindex actions, time to replay index actions.
        self.activate(passive_commit=1, priority=5).\
            playBackRecordedObjectList(sql_catalog_id=sql_catalog_id,
                                       catalog=1)
      # If we were replaying index actions, there is nothing else to do.

  def changeSQLConnectionIds(self, folder, sql_connection_id_dict):
    if sql_connection_id_dict is not None:
      if folder.meta_type == 'Z SQL Method':
        connection_id = folder.connection_id
        if connection_id in sql_connection_id_dict:
          folder.connection_id = sql_connection_id_dict[connection_id]
      elif getattr(aq_base(folder), 'objectValues', _marker) is not _marker:
        for object in folder.objectValues():
          self.changeSQLConnectionIds(object,sql_connection_id_dict)

  def exchangeDatabases(self, source_sql_catalog_id, destination_sql_catalog_id,
                        skin_selection_dict, sql_connection_id_dict):
    """
      Exchange two databases.
    """
    if self.default_sql_catalog_id == source_sql_catalog_id:
      self.default_sql_catalog_id = destination_sql_catalog_id
      # Insert the latest generated uid.
      # This must be done just before swaping the catalogs in case there were
      # generated uids since destination catalog was created.
      self[destination_sql_catalog_id].insertMaxUid()

    LOG('exchangeDatabases skin_selection_dict:',0,skin_selection_dict)
    if skin_selection_dict is not None:
      #LOG('exchangeDatabases skin_selection_dict:',0,'we will do manage_skinLayers')
      for skin_name, selection in self.portal_skins.getSkinPaths():
        if skin_name in skin_selection_dict:
          new_selection = tuple(skin_selection_dict[skin_name])
          self.portal_skins.manage_skinLayers(skinpath = new_selection, skinname = skin_name, add_skin = 1)

    LOG('exchangeDatabases sql_connection_id_dict :',0,sql_connection_id_dict)
    if sql_connection_id_dict is not None:
      self.changeSQLConnectionIds(self.portal_skins, sql_connection_id_dict)

  def manage_hotReindexAll(self, source_sql_catalog_id,
                           destination_sql_catalog_id,
                           archive_path=None,
                           source_sql_connection_id_list=None,
                           destination_sql_connection_id_list=None,
                           skin_name_list=None,
                           skin_selection_list=None,
                           update_destination_sql_catalog=None,
                           REQUEST=None, RESPONSE=None):
    """
      Starts a hot reindexing.

      Hot reindexing will create a catalog and sync it with the current one.
      Once done, both catalogs will be swapped so that current catalog will
      not be used any more and destination catalog will get used "for real".

      source_catalog_id
        Id of the SQLCatalog object to use as the source catalog.
        WARNING: it is not considered normal to specify a catalog which is not
                 the current default one.
                 The feature is still provided, but you'll be on your own if
                 you try it.

      destination_sql_catalog_id 
        Id of the SQLCatalog object to use as the new catalog.

      source_sql_connection_id_list
      destination_sql_connection_id_list
        SQL Methods in portal_skins using source_sql_connection_id_list[n]
        connection will use destination_sql_connection_id_list[n] connection
        once hot reindexing is over.

      skin_name_list
      skin_selection_list
        For each skin_name_list[n], skin_selection_list[n] will be set to
        replace the existing skin selection on portal_skins.
    """
    # Hot reindexing can only be runing once at a time on a system.
    if self.hot_reindexing_state is not None:
      raise CatalogError, 'hot reindexing process is already running %s -%s' %(self, self.hot_reindexing_state)

    if source_sql_catalog_id == destination_sql_catalog_id:
      raise CatalogError, 'Hot reindexing cannot be done with the same '\
                          'catalog as both source and destination. What'\
                          ' you want to do is a "clear catalog" and an '\
                          '"ERP5Site_reindexAll".'

    if source_sql_catalog_id != self.default_sql_catalog_id:
      LOG('ZSQLCatalog', 0, 'Warning : Hot reindexing is started with a '\
                            'source catalog which is not the default one.')

    # Construct a mapping for skin selections. It will be used during the
    # final hot reindexing step.
    skin_selection_dict = None
    if skin_name_list is not None and skin_selection_list is not None:
      skin_selection_dict = {}
      for name, selection_list in zip(skin_name_list, skin_selection_list):
        # Make sure that there is no extra space.
        new_selection_list = []
        for selection in selection_list:
          new_selection = selection.strip()
          if len(new_selection) > 0:
            new_selection_list.append(new_selection)
        skin_selection_dict[name] = new_selection_list

    # Construct a mapping for connection ids. It will be used during the
    # final hot reindexing step.
    sql_connection_id_dict = None
    if source_sql_connection_id_list is not None and \
       destination_sql_connection_id_list is not None:
      sql_connection_id_dict = {}
      for source_sql_connection_id, destination_sql_connection_id in \
          zip(source_sql_connection_id_list,
              destination_sql_connection_id_list):
        if source_sql_connection_id != destination_sql_connection_id:
          sql_connection_id_dict[source_sql_connection_id] = \
              destination_sql_connection_id

    destination_sql_catalog = getattr(self,destination_sql_catalog_id)
    if update_destination_sql_catalog:
      self.changeSQLConnectionIds(destination_sql_catalog,
                                  sql_connection_id_dict)

    # First of all, make sure that all root objects have uids.
    # XXX This is a workaround for tools (such as portal_simulation).
    portal = self.getPortalObject()
    for id in portal.objectIds():
      getUid = getattr(portal[id], 'getUid', None)
      if getUid is not None and id != "portal_uidhandler":
        # XXX check adviced by yo, getUid is different for this tool
        getUid() # Trigger the uid generation if none is set.

    # Mark the hot reindex as begun. Each object indexed in the still-current
    # catalog will be scheduled for reindex in the future catalog.
    LOG('hotReindexObjectList', 0, 'Starting recording')
    self.setHotReindexingState(HOT_REINDEXING_RECORDING_STATE,
                               source_sql_catalog_id=source_sql_catalog_id,
                               destination_sql_catalog_id=destination_sql_catalog_id,
                               archive_path=archive_path)
    # Clear the future catalog and start reindexing the site in it.
    final_activity_tag = 'hot_reindex_last_ERP5Site_reindexAll_tag'
    self.ERP5Site_reindexAll(sql_catalog_id=destination_sql_catalog_id,
                             final_activity_tag=final_activity_tag,
                             clear_catalog=1,
                             passive_commit=1)
    # Once reindexing is finished, change the hot reindexing state so that
    # new catalog changes are applied in both catalogs.
    self.activate(passive_commit=1,
                  after_tag=final_activity_tag,
                  priority=5).setHotReindexingState(HOT_REINDEXING_DOUBLE_INDEXING_STATE,
                      source_sql_catalog_id=source_sql_catalog_id,
                      destination_sql_catalog_id=destination_sql_catalog_id)
    # Once in double-indexing mode, planned reindex can be replayed.
    self.activate(passive_commit=1,
                  after_method_id='setHotReindexingState',
                  priority=5).playBackRecordedObjectList(
                      sql_catalog_id=destination_sql_catalog_id)
    # Once there is nothing to replay, databases are sync'ed, so the new
    # catalog can become current.
    self.activate(passive_commit=1,
                  after_method_id=('playBackRecordedObjectList', 'runInventoryMethod'),
                  after_tag='runInventoryMethod',
                  priority=5).finishHotReindexing(
                      source_sql_catalog_id=source_sql_catalog_id,
                      destination_sql_catalog_id=destination_sql_catalog_id,
                      skin_selection_dict=skin_selection_dict,
                      sql_connection_id_dict=sql_connection_id_dict)
    if RESPONSE is not None:
      URL1 = REQUEST.get('URL1')
      RESPONSE.redirect(URL1 + '/manage_catalogHotReindexing?manage_tabs_message=HotReindexing%20Started')

  def manage_edit(self, RESPONSE, URL1, threshold=1000, REQUEST=None):
    """ edit the catalog """
    if type(threshold) is not type(1):
      threshold=string.atoi(threshold)
    self.threshold = threshold

    RESPONSE.redirect(URL1 + '/manage_main?manage_tabs_message=Catalog%20Changed')


  def manage_catalogObject(self, REQUEST, RESPONSE, URL1, urls=None, sql_catalog_id=None):
    """ index Zope object(s) that 'urls' point to """
    if sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.manage_catalogObject(REQUEST, RESPONSE, URL1, urls=urls)


  def manage_uncatalogObject(self, REQUEST, RESPONSE, URL1, urls=None, sql_catalog_id=None):
    """ removes Zope object(s) 'urls' from catalog """
    if sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.manage_uncatalogObject(REQUEST, RESPONSE, URL1, urls=urls)


  def manage_catalogReindex(self, REQUEST, RESPONSE, URL1, urls=None, sql_catalog_id=None):
    """ clear the catalog, then re-index everything """
    if sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.manage_catalogReindex(REQUEST, RESPONSE, URL1, urls=urls)

  def refreshCatalog(self, clear=0, sql_catalog_id=None):
    """ re-index everything we can find """

    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      paths = catalog.getPaths()
      if clear:
        catalog.clear()

      for p in paths:
        obj = self.resolve_path(p.path)
        if not obj:
          obj = self.resolve_url(p.path, self.REQUEST)
        if obj is not None:
          self.catalog_object(obj, p.path, sql_catalog_id=sql_catalog_id)

  def manage_catalogClear(self, REQUEST=None, RESPONSE=None, URL1=None, sql_catalog_id=None):
    """ clears the whole enchilada """
    if REQUEST is not None and sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.manage_catalogClear(REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL1)

  def manage_catalogClearReserved(self, REQUEST=None, RESPONSE=None, URL1=None, sql_catalog_id=None):
    """ clears the whole enchilada """
    if REQUEST is not None and sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.manage_catalogClearReserved(REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL1)

  def manage_catalogFoundItems(self, REQUEST, RESPONSE, URL2, URL1,
                 obj_metatypes=None,
                 obj_ids=None, obj_searchterm=None,
                 obj_expr=None, obj_mtime=None,
                 obj_mspec=None, obj_roles=None,
                 obj_permission=None,
                 sql_catalog_id=None):
    """ Find object according to search criteria and Catalog them
    """
    if sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.manage_catalogFoundItems(REQUEST, RESPONSE, URL2, URL1,
                                       obj_metatypes=obj_metatypes, obj_ids=obj_ids,
                                       obj_searchterm=obj_searchterm, obj_expr=obj_expr,
                                       obj_mtime=obj_mtime, obj_mspec=obj_mspec,
                                       obj_roles=obj_roles, obj_permission=obj_permission)

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
                    apply_path=path,
                    sql_catalog_id=sql_catalog_id)

    elapse = time.time() - elapse
    c_elapse = time.clock() - c_elapse

    RESPONSE.redirect(URL1 + '/manage_catalogView?manage_tabs_message=' +
              urllib.quote('Catalog Updated<br>Total time: %s<br>Total CPU time: %s' % (`elapse`, `c_elapse`)))

  def manage_editSchema(self, names, REQUEST=None, RESPONSE=None, URL1=None, sql_catalog_id=None):
    """ add a column """
    if REQUEST is not None and sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    self.editSchema(names, sql_catalog_id=sql_catalog_id)

    if REQUEST and RESPONSE:
      RESPONSE.redirect(URL1 + '/manage_catalogSchema?manage_tabs_message=Schema%20Saved')

  def newUid(self, sql_catalog_id=None):
    """
        Allocates a new uid value.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.newUid()

  def getDynamicRelatedKeyList(self, sql_catalog_id=None,**kw):
    """
    Return the list of dynamic related keys.
    """
    return []

  def wrapObject(self, object, **kw):
    """
      Return a wrapped object for reindexing.

      This method should be overridden if necessary.
    """
    #LOG('ZSQLCatalog wrapObject', 0, 'object = %r, kw = %r' % (object, kw))
    return object

  def catalog_object(self, obj, url=None, idxs=[], is_object_moved=0, sql_catalog_id=None, **kw):
    """ wrapper around catalog """
    self.catalogObjectList([obj], sql_catalog_id=sql_catalog_id)

  def catalogObjectList(self, object_list, sql_catalog_id=None, disable_archive=0, **kw):
    """Catalog a list of objects.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    default_catalog = self.getSQLCatalog()
    hot_reindexing = (self.hot_reindexing_state is not None) and \
                     (catalog is not None) and \
                     (self.source_sql_catalog_id == catalog.id)
    archiving = self.archive_path is not None
    wrapped_object_list = []
    failed_object_list = []
    url_list = []
    if getattr(self, "portal_archives", None) is not None:
      archive_list = self.portal_archives.getArchiveList()
    else:
      archive_list = []

    catalog_dict = {}

    # Create archive obj list if necessary
    if archiving:
      # while archiving only test with the archive we used, do not care
      # of other as they must alredy be ok
      archive = self.unrestrictedTraverse(self.archive_path)
      archive_obj_list = [archive,]
      for archive_path in archive_list:
        try:
          archive = self.unrestrictedTraverse(archive_path)
        except KeyError:
          continue
        if archive.getCatalogId() == self.destination_sql_catalog_id:
          archive_obj_list.append(archive)
    else:
      # otherwise take all archive in use to knwo where object must go
      archive_obj_list = []
      for archive_path in archive_list:
        try:
          archive = self.unrestrictedTraverse(archive_path)
        except KeyError:
          continue
        archive_obj_list.append(archive)
    # Construct list of object to catalogged
    for obj in object_list:
      if hot_reindexing:
        try: 
          url = obj.getPhysicalPath
        except AttributeError:
          raise CatalogError(
            "A cataloged object must support the 'getPhysicalPath' "
            "method if no unique id is provided when cataloging"
            )
        url = '/'.join(url())
        url_list.append(url)
        
      goto_current_catalog = 0
      if (not disable_archive) and (archiving or (len(archive_obj_list) > 0 and \
                                                 (sql_catalog_id == default_catalog.id or \
                                                  sql_catalog_id is None))):
        # check in which archive object must go if we defined archive
        catalog_id = None
        for archive in archive_obj_list:
          if archive.test(obj) is True:
            goto_current_catalog = 0
            catalog_id = archive.getCatalogId()
            priority = archive.getPriority()
            if catalog_dict.has_key(catalog_id):
              catalog_dict[catalog_id]['obj'].append(obj)
            else:
              catalog_dict[catalog_id] = {'priority' : priority, 'obj' : [obj,]}
        if catalog_id is None or sql_catalog_id is None or self.source_sql_catalog_id == catalog.id:
          # at least put object in current catalog if no archive match
          goto_current_catalog = 1
      else:
        goto_current_catalog = 1

      if goto_current_catalog:
        try:
          # wrap object only when sure it will be reindex now
          # thus security uid is also reindex
          wrap_obj = self.wrapObject(obj, sql_catalog_id=sql_catalog_id)
        except ConflictError:
          raise
        except:
          LOG('WARNING ZSQLCatalog', 0, 'wrapObject failed on the object %r' % (obj,), error=sys.exc_info())
          failed_object_list.append(obj)
        wrapped_object_list.append(wrap_obj)
      
    # run activity or execute for each archive depending on priority
    if len(catalog_dict):
      for catalog_id in catalog_dict.keys():
        if goto_current_catalog and catalog_id == default_catalog.id:
          # if we reindex in current catalog, do not relaunch an activity for this
          continue
        d = catalog_dict[catalog_id]
        # hot_reindexing is True when creating an object during a hot reindex, in this case, we don't want
        # to reindex it in destination catalog, it will be recorded an play only once
        if not hot_reindexing and self.hot_reindexing_state != HOT_REINDEXING_DOUBLE_INDEXING_STATE and \
               self.destination_sql_catalog_id == catalog_id:
          destination_catalog = self.getSQLCatalog(self.destination_sql_catalog_id)
          # wrap all objects
          wrapped_object_list_2 = []
          for obj in d['obj']:
            try:
              wrap_obj = self.wrapObject(obj, sql_catalog_id=catalog_id)
            except ConflictError:
              raise
            except:
              LOG('WARNING ZSQLCatalog', 0, 'wrapObject failed on the object %r' % (obj,), error=sys.exc_info())
              failed_object_list.append(obj)
            wrapped_object_list_2.append(wrap_obj)
          # reindex objects in destination catalog
          destination_catalog.catalogObjectList(wrapped_object_list_2, **kw)
        else:
          for obj in d['obj']:
            obj._reindexObject(sql_catalog_id=catalog_id, activate_kw = \
                              {'priority': d['priority']}, disable_archive=1, **kw)
    
    if catalog is not None:
      if len(wrapped_object_list):
        catalog.catalogObjectList(wrapped_object_list, **kw)
      if hot_reindexing:
        destination_catalog = self.getSQLCatalog(self.destination_sql_catalog_id)
        if destination_catalog.id != catalog.id:
          if self.hot_reindexing_state == HOT_REINDEXING_RECORDING_STATE:
            destination_catalog.recordObjectList(url_list, 1)
          else:
            if len(wrapped_object_list):
              destination_catalog.catalogObjectList(wrapped_object_list,**kw)

    object_list[:] = failed_object_list[:]
          

  def uncatalog_object(self, uid=None,path=None, sql_catalog_id=None):
    """ wrapper around catalog """
    if uid is None:
      raise TypeError, "sorry uncatalog_object supports only uid"

    if getattr(self, "portal_archives", None) is not None:
      archive_list = self.portal_archives.getArchiveList()
    else:
      archive_list = []
    catalog_id = None
    if len(archive_list) and sql_catalog_id is None:
      for archive_path in archive_list:
        try:
          archive = self.unrestrictedTraverse(archive_path)
        except KeyError:
          continue
        catalog_id = archive.getCatalogId()
        self.activate(activity="SQLQueue",
                      priority=archive.getPriority()).uncatalog_object(uid=uid,path=path,
                                                                      sql_catalog_id=catalog_id)
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None and catalog_id is None:
      catalog.uncatalogObject(uid=uid,path=path)
      if self.hot_reindexing_state is not None and self.source_sql_catalog_id == catalog.id:
        destination_catalog = self.getSQLCatalog(self.destination_sql_catalog_id)
        if destination_catalog.id != catalog.id:
          if self.hot_reindexing_state == HOT_REINDEXING_RECORDING_STATE:
            destination_catalog.recordObjectList([uid], 0)
          else:
            destination_catalog.uncatalogObject(uid=uid)


  def beforeUncatalogObject(self, uid=None,path=None, sql_catalog_id=None):
    """ wrapper around catalog """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.beforeUncatalogObject(uid=uid,path=path)

  def beforeCatalogClear(self):
    """ allow to override this method """
    pass

  def catalogTranslationList(self, object_list, sql_catalog_id=None):
    """Catalog translations.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.catalogTranslationList(object_list)

  def deleteTranslationList(self, sql_catalog_id=None):
    """Delete translations.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.deleteTranslationList()

  def uniqueValuesFor(self, name, sql_catalog_id=None):
    """ returns the unique values for a given FieldIndex """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.uniqueValuesFor(name)

    return ()

  def getpath(self, uid, sql_catalog_id=None):
    """
    Return the path to a cataloged object given its uid
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      object = catalog[uid]
      if object is not None:
        return object.path
      else:
        return None
  getPath = getpath

  def hasPath(self, path, sql_catalog_id=None):
    """
    Checks if path is catalogued
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.hasPath(path)

  def getobject(self, uid, REQUEST=None, sql_catalog_id=None):
    """
    Return a cataloged object given its uid
    """
    if REQUEST is not None and sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    path = self.getpath(uid, sql_catalog_id=sql_catalog_id)
    obj = self.aq_parent.unrestrictedTraverse(path)
    if obj is None:
      if REQUEST is None:
        REQUEST=self.REQUEST
      obj = self.resolve_url(path, REQUEST)
    return obj
  getObject = getobject

  def getObjectList(self, uid_list, REQUEST=None, sql_catalog_id=None):
    """
    Return a cataloged object given its uid
    """
    obj_list = []
    for uid in uid_list:
      obj_list.append(self.getObject(uid, REQUEST, sql_catalog_id=sql_catalog_id))
    return obj_list

  def getMetadataForUid(self, rid, sql_catalog_id=None):
    """return the correct metadata for the cataloged uid"""
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.getMetadataForUid(int(rid))
    return {}

  def getIndexDataForUid(self, rid, sql_catalog_id=None):
    """return the current index contents for the specific uid"""
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.getIndexDataForUid(rid)
    return {}

  # Aliases
  getMetadataForRID = getMetadataForUid
  getIndexDataForRID = getIndexDataForUid

  def schema(self, sql_catalog_id=None):
    return self.getColumnIds(sql_catalog_id=sql_catalog_id)

  def indexes(self, sql_catalog_id=None):
    return self.getColumnIds(sql_catalog_id=sql_catalog_id)

  def names(self, sql_catalog_id=None):
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.names
    return {}

  def getColumnIds(self, sql_catalog_id=None):
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.getColumnIds()
    return []

  def getAttributesForColumn(self, column, sql_catalog_id=None):
    """
      Return the attribute names as a single string
    """
    return string.join(self.names(sql_catalog_id=sql_catalog_id).get(column, ('',)),' ')

  def _searchable_arguments(self, sql_catalog_id=None):
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.getColumnIds(sql_catalog_id=sql_catalog_id)
    return []

  def editSchema(self,names, sql_catalog_id=None):
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.editSchema(names)

  def _searchable_result_columns(self, sql_catalog_id=None):
    r = []
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      for name in catalog.getColumnIds():
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

  security.declarePublic('buildSQLQuery')
  def buildSQLQuery(self, REQUEST=None, query_table='catalog', sql_catalog_id=None, **kw):
    """
      Build a SQL query from keywords.
      If query_table is specified, it is used as the table name instead of 'catalog'.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.buildSQLQuery(REQUEST=REQUEST, query_table=query_table, **kw)
    return ''

  # Compatibility SQL Sql
  security.declarePublic('buildSqlQuery')
  buildSqlQuery = buildSQLQuery

  def searchResults(self, REQUEST=None, used=None, sql_catalog_id=None, **kw):
    """
    Search the catalog according to the ZTables search interface.
    Search terms can be passed in the REQUEST or as keyword
    arguments.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return apply(catalog.searchResults, (REQUEST,used), kw)
    return []

  __call__=searchResults

  def countResults(self, REQUEST=None, used=None, sql_catalog_id=None, **kw):
    """
    Counts the number of items which satisfy the query defined in kw.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return apply(catalog.countResults, (REQUEST,used), kw)
    return []

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
             apply_func=None, apply_path='',
             sql_catalog_id=None):
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
    except AttributeError:
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
          apply_func(ob, (apply_path+'/'+p), sql_catalog_id=sql_catalog_id)
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
                    apply_func, apply_path,
                    sql_catalog_id)
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
    try: 
      return REQUEST.resolve_url(path)
    except ConflictError: 
      raise
    except: 
      pass

  def resolve_path(self, path):
    """
    Attempt to resolve a url into an object in the Zope
    namespace. The url may be absolute or a catalog path
    style url. If no object is found, None is returned.
    No exceptions are raised.
    """
    try: 
      return self.unrestrictedTraverse(path)
    except ConflictError:
      raise
    except: 
      pass

  def manage_normalize_paths(self, REQUEST, sql_catalog_id=None):
    """Ensure that all catalog paths are full physical paths

    This should only be used with ZCatalogs in which all paths can
    be resolved with unrestrictedTraverse."""

    if sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      paths = catalog.paths
      uids = catalog.uids
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
        self.uncatalog_object(path, sql_catalog_id=sql_catalog_id)

    return MessageDialog(title='Done Normalizing Paths',
      message='%s paths normalized, %s paths removed, and '
          '%s unchanged.' % (len(fixed), len(removed), unchanged),
      action='./manage_main')

  def getTableIds(self, sql_catalog_id=None):
    """Returns all tables of this catalog
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.getTableIds()
    return []

  def getCatalogSearchResultKeys(self, sql_catalog_id=None):
    """Return selected tables of catalog which are used in JOIN.
       catalaog is always first
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.sql_search_result_keys
    return []

  def getCatalogSearchTableIds(self, sql_catalog_id=None):
    """Return selected tables of catalog which are used in JOIN.
       catalaog is always first
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.getCatalogSearchTableIds()
    return []

  def getResultColumnIds(self, sql_catalog_id=None):
    """Return selected tables of catalog which are used
       as metadata
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.getResultColumnIds()
    return []

  def getCatalogMethodIds(self, sql_catalog_id=None):
    """Find Z SQL methods in the current folder and above
    This function return a list of ids.
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.getCatalogMethodIds()
    return {}

  def manage_editFilter(self, REQUEST=None, RESPONSE=None, URL1=None, sql_catalog_id=None):
    """
    This methods allows to set a filter on each zsql method called,
    so we can test if we should or not call a zsql method, so we can
    increase a lot the speed.
    """
    if REQUEST is not None and sql_catalog_id is None:
      sql_catalog_id = REQUEST.get('sql_catalog_id', None)

    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      catalog.manage_editFilter(REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL1)

  def getFilterableMethodList(self, sql_catalog_id=None):
    """
    Returns only zsql methods wich catalog or uncatalog objets
    """
    catalog = self.getSQLCatalog(sql_catalog_id)
    if catalog is not None:
      return catalog.getFilterableMethodList()
    return []


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
