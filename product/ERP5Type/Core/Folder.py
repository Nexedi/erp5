# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import transaction
from collections import deque
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.ZopeGuards import NullIter
from Acquisition import aq_base, aq_parent, aq_inner
from OFS.ObjectManager import ObjectManager, checkValidId
from zExceptions import BadRequest
from OFS.History import Historical
import ExtensionClass

from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.PortalFolder import ContentFilter

from Products.ERP5Type.Base import Base
from Products.ERP5Type.CopySupport import CopyContainer
from Products.ERP5Type import PropertySheet
from Products.ERP5Type.XMLExportImport import Folder_asXML
from Products.ERP5Type.Utils import sortValueList
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Accessor import Base as BaseAccessor

try:
  from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder
except ImportError:
  from Products.BTreeFolder2.CMFBTreeFolder import CMFBTreeFolder

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base, BTreeFolder2

try:
  from Products.HBTreeFolder2.CMFHBTreeFolder import CMFHBTreeFolder
  from Products.HBTreeFolder2.HBTreeFolder2 import HBTreeFolder2Base
  from Products.HBTreeFolder2.HBTreeFolder2 import HBTreeFolder2
except ImportError:

  class CMFHBTreeFolder:
    pass

  class HBTreeFolder2Base:
    pass

  class HBTreeFolder2:
    pass


from DateTime import DateTime
from random import randint


import os

from zLOG import LOG, WARNING
import warnings

# variable to inform about migration process
migration_process_lock = "_migration_in_progress"

REINDEX_SPLIT_COUNT = 100 # if folder containes more than this, reindexing should be splitted.
from Products.ERP5Type.Message import translateString

# from Products.BTreeFolder2.BTreeFolder2 import _marker as BTreeMarker
# from Products.HBTreeFolder2.HBTreeFolder2 import _marker as HBTreeMarker

# Dummy Functions for update / upgrade
def dummyFilter(object,REQUEST=None):
  return 1

def dummyTestAfter(object,REQUEST=None):
  return []

class FolderMixIn(ExtensionClass.Base):
  """A mixin class for folder operations, add content, delete content etc.
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declarePublic('isTempObject')
  def isTempObject(self):
    """Return true if self is an instance of a temporary document class.
    """
    # Note: Folder inherits from Base and FolderMixIn but Base has priority.
    return 0

  security.declarePublic('newContent')
  def newContent(self, id=None, portal_type=None, id_group=None,
          default=None, method=None, container=None, temp_object=0, **kw):
    """Creates a new content.
    This method is public, since TypeInformation.constructInstance will perform
    the security check.
    """
    pt = self._getTypesTool()
    if container is None:
      container = self
    temp_container = container.isTempObject()

    # The only case where the id is unused (because the new object is not added
    # to its parent) is when a temp object is created inside a non-temp object.
    if id is None and (temp_container or not temp_object):
      new_id_kw = {}
      if method is not None:
        new_id_kw['method'] = method
      new_id = str(container.generateNewId(id_group=id_group,
                                           default=default,
                                           **new_id_kw))
    else:
      new_id = str(id)

    if portal_type is None:
      # XXX This feature is very confusing
      # And made the code more difficult to update
      allowed_content_type_list = container.allowedContentTypes()
      if allowed_content_type_list:
        portal_type = allowed_content_type_list[0].id
      else:
        raise ValueError('Creation disallowed')
    else:
      type_info = pt.getTypeInfo(container)
      if type_info is not None and not type_info.allowType(portal_type) and \
          'portal_trash' not in container.getPhysicalPath():
        raise ValueError('Disallowed subobject type: %s on %r' % (portal_type, container))

    type_info = pt.getTypeInfo(portal_type)
    if type_info is None:
      raise ValueError('No such content type: %s' % portal_type)

    new_instance = type_info.constructInstance(
                           container=container,
                           id=new_id,
                           temp_object=temp_object or temp_container,
                           **kw)
    if temp_container:
      container._setObject(new_instance.id, new_instance.aq_base)
    return new_instance

  security.declareProtected(
            Permissions.DeletePortalContent, 'deleteContent')
  def deleteContent(self, id):
    """ delete items in this folder.
      `id` can be a list or a string.
    """
    error_message = 'deleteContent only accepts string or list of strings not '
    if isinstance(id, str):
      self._delObject(id)
    elif isinstance(id, (list, tuple)):
      for my_id in id:
        if isinstance(my_id, str):
          self._delObject(my_id)
        else:
          raise TypeError, error_message + str(type(my_id))
    else:
      raise TypeError, error_message + str(type(id))

  def _generatePerDayId(self):
    """
    Generate id base on date, useful for HBTreeFolder
    We also append random id
    """
    current_date = DateTime().strftime('%Y%m%d')
    my_id = self._generateRandomId()
    return "%s-%s" %(current_date, my_id)

  def _generateRandomId(self):
    """
      Generate a random Id.
      10000 factor makes the odd to generate an already existing Id of 1 out
      of 10000, not depending on the number of objects present in this folder.
      len(self)+1 to make sure generation works on an empty Folder.
    """
    return '%X' % (randint(1, 10000 * (len(self) + 1)), )

  def _generateNextId(self):
    """
      Get the last generated Id, increment it until no object with generated
      Id exist, then save the Id.
    """
    try:
      my_id = int(self.getLastId()) + 1
    except TypeError:
      my_id = 1
    while self.hasContent(str(my_id)):
      my_id = my_id + 1
    my_id = str(my_id)
    self._setLastId(my_id) # Make sure no reindexing happens
    return my_id

  def _generatePerNodeId(self):
    """
    Generate id base on the node id defined in the zope.conf,
    useful for import and mass creation
    of objects inside a module using activities
    We also append random id
    """
    activity_tool = self.getPortalObject().portal_activities
    new_id = "%s-%s" %(activity_tool.getCurrentNode().replace("-", "_"),
                       self._generateRandomId())
    try:
       checkValidId(self, new_id)
    except BadRequest:
      return self._generateNextId()
    return new_id

  def _generatePerNodeNumberId(self):
    """
    Generate id base on node number, useful for import and mass creation
    of objects inside a module using activities
    We also append random id
    """
    activity_tool = self.getPortalObject().portal_activities
    node_list = list(activity_tool.getNodeList())
    current_node = activity_tool.getCurrentNode()
    try:
      node_number = node_list.index(current_node) + 1
    except ValueError:
      # Not a processing node
      node_number = 0
    return "%03d-%s" %(node_number, self._generateRandomId())

  def _generatePerDayNodeNumberId(self):
    """
    Generate id base on date and node number, useful for import and mass
    creation of objects inside a module using activities. We also append
    random id.
    """
    activity_tool = self.getPortalObject().portal_activities
    node_list = list(activity_tool.getNodeList())
    current_node = activity_tool.getCurrentNode()
    try:
      node_number = node_list.index(current_node) + 1
    except ValueError:
      # Not a processing node
      node_number = 0
    current_date = DateTime().strftime('%Y%m%d')
    my_id = self._generateRandomId()
    return "%s.%03d-%s" %(current_date, node_number, my_id)

  # Getter defines to address migration of a site to ZODB Property Sheets,
  # otherwise installing erp5_property_sheets fails in generateNewId() as
  # getIdGenerator accessor does not exist yet
  getIdGenerator = BaseAccessor.Getter('getIdGenerator', 'id_generator',
                                       'string', default='')

  getLastId = BaseAccessor.Getter('getLastId', 'last_id', 'string',
                                  default='0')

  _setLastId = BaseAccessor.Setter('_setLastId', 'last_id', 'string')

  # Automatic ID Generation method
  security.declareProtected(Permissions.View, 'generateNewId')
  def generateNewId(self,id_group=None,default=None,method=None):
    """
      Generate a new Id which has not been taken yet in this folder.
      Eventually increment the id number until an available id
      can be found

      Permission is view because we may want to add content to a folder
      without changing the folder content itself.
    """
    my_id = None
    if id_group is None:
      id_group = self.getIdGroup()
    if id_group in (None, 'None'):
      id_generator = self.getIdGenerator()
      if not isinstance(id_generator, str):
        LOG('Folder.generateNewId', 0, '%s.id_generator is not a string.'
            ' Falling back on default behaviour.' % (self.absolute_url(), ))
        id_generator = ''
      if id_generator != '':
        # Custom aq_dynamic function (like the one defined on WebSite objects)
        # can find an object which has no name. So we must recognise the
        # default value of id_generator and force safe fallback in this case.
        idGenerator = getattr(self, id_generator, None)
        if idGenerator is None:
          raise ValueError("Could not find id_generator %r" % (id_generator,))
      else:
        idGenerator = self._generateNextId
      my_id = idGenerator()
      while self.hasContent(my_id):
        my_id = idGenerator()
    else:
      new_id_kw = {}
      if method is not None:
        new_id_kw['method'] = method
      my_id = str(self.portal_ids.generateNewId(id_generator='document',
                  id_group=id_group, default=default, **new_id_kw))
    return my_id

  security.declareProtected(Permissions.View, 'hasContent')
  def hasContent(self, id):
    return self.hasObject(id)

  # Get the content
  security.declareProtected(Permissions.AccessContentsInformation, 'searchFolder')
  def searchFolder(self, **kw):
    """
      Search the content of a folder by calling
      the portal_catalog.
    """
    kw['parent_uid'] = self.getUid()

    # Make sure that if we use parent base category
    # We do not have conflicting parent uid values
    delete_parent_uid = 0
    if kw.has_key('selection_domain'):
      if not isinstance(kw['selection_domain'], dict):
        warnings.warn("To pass a DomainSelection instance is deprecated.\n"
                      "Please use a domain dict instead.",
                      DeprecationWarning)
        kw['selection_domain'] = kw['selection_domain'].asDomainDict()
      if kw['selection_domain'].has_key('parent'):
        delete_parent_uid = 1
    if kw.has_key('selection_report'):
      if not isinstance(kw['selection_report'], dict):
        warnings.warn("To pass a DomainSelection instance is deprecated.\n"
                      "Please use a domain dict instead.",
                      DeprecationWarning)
        kw['selection_report'] = kw['selection_report'].asDomainDict()
      if kw['selection_report'].has_key('parent'):
        delete_parent_uid = 1
    if delete_parent_uid:
      del kw['parent_uid']

    return self.portal_catalog.searchResults(**kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'countFolder')
  def countFolder(self, **kw):
    """
      Search the content of a folder by calling
      the portal_catalog.
    """
    kw['parent_uid'] = self.getUid()

    # Make sure that if we use parent base category
    # We do not have conflicting parent uid values
    delete_parent_uid = 0
    if kw.has_key('selection_domain'):
      if not isinstance(kw['selection_domain'], dict):
        warnings.warn("To pass a DomainSelection instance is deprecated.\n"
                      "Please use a domain dict instead.",
                      DeprecationWarning)
        kw['selection_domain'] = kw['selection_domain'].asDomainDict()
      if kw['selection_domain'].has_key('parent'):
        delete_parent_uid = 1
    if kw.has_key('selection_report'):
      if not isinstance(kw['selection_report'], dict):
        warnings.warn("To pass a DomainSelection instance is deprecated.\n"
                      "Please use a domain dict instead.",
                      DeprecationWarning)
        kw['selection_report'] = kw['selection_report'].asDomainDict()
      if kw['selection_report'].has_key('parent'):
        delete_parent_uid = 1
    if delete_parent_uid:
      del kw['parent_uid']

    return self.portal_catalog.countResults(**kw)

  # Count objects in the folder
  security.declarePrivate('_count')
  def _count(self, **kw):
    """
      Returns the number of items in the folder.
    """
    return self.countFolder(**kw)[0][0]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getWebSiteValue')
  def getWebSiteValue(self):
    """
    Since aq_dynamic will not work well to get Web Site for language
    specified case (eg. web_site_module/site/fr/web_page_module), we
    call aq_parent instead to reach the Web Site.
    """
    getWebSiteValue = getattr(aq_parent(self), 'getWebSiteValue', None)
    if getWebSiteValue is not None:
      return getWebSiteValue()
    else:
      return None

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getWebSectionValue')
  def getWebSectionValue(self):
    """
    Since aq_dynamic will not work well to get Web Section for language
    specified case (eg. web_site_module/site/fr/section/web_page_module),
    we call aq_parent instead to reach the Web Section.
    """
    getWebSectionValue = getattr(aq_parent(self), 'getWebSectionValue', None)
    if getWebSectionValue is not None:
      return getWebSectionValue()
    else:
      return None

  def _recurseCallMethod(self, method_id, method_args=(), method_kw={},
                         restricted=False, id_list=None, min_id=None, **kw):
    """Run a script by activity on objects found recursively from this folder

    This method is configurable (via activate_kw['group_*'] & 'activity_count'
    parameters) so that it can work efficiently with databases of any size.

    'activate_kw' may specify an active process to collect results.

    In order to activate objects that don't inherit ActiveObject,
    only placeless default activate parameters are taken into account.
    """
    activate_kw = self.getDefaultActivateParameterDict.im_func(None)
    activate_kw.update(kw.get('activate_kw', ()))
    activate_kw.setdefault('active_process', None)
    activate = self.getPortalObject().portal_activities.activateObject
    validate = restricted and getSecurityManager().validate
    cost = activate_kw.setdefault('group_method_cost', .034) # 30 objects
    if cost != 1:
      activate_kw.setdefault('group_method_id', None) # dummy group method
    activity_count = kw.get('activity_count', 1000)
    if activity_count is None:
      check_limit = lambda: None
    else:
      check_limit = iter(xrange(activity_count)).next
    try:
      recurse_stack = kw['_recurse_stack']
    except KeyError:
      recurse_stack = [deque(id_list) if id_list else min_id or '']
      kw['_recurse_stack'] = recurse_stack
    min_depth = kw.get('min_depth', 0)
    max_depth = kw.get('max_depth', 0)
    def recurse(container, depth):
      if getattr(aq_base(container), 'getPhysicalPath', None) is None:
        return
      if (max_depth is None or depth < max_depth) and \
         isinstance(container, ObjectManager) and len(container):
        try:
          next_id = recurse_stack[depth]
        except IndexError:
          next_id = ''
          recurse_stack.append(next_id)
        if isinstance(next_id, basestring):
          folder_handler = isinstance(container, Folder) and \
                          container._folder_handler
          if not folder_handler:
            next_id = deque(x for x in container.objectIds() if x >= next_id)
            recurse_stack[depth] = next_id
          else:
            for id, ob in container.iteritems(next_id):
              if not restricted or validate(container, container, id, ob):
                recurse_stack[depth] = id
                recurse(ob, depth + 1)
            recurse_stack[-1] = next_id = None
        while next_id:
          id = next_id[0]
          ob = container._getOb(id)
          if not restricted or validate(container, container, id, ob):
            recurse(ob, depth + 1)
          del next_id[0]
      if min_depth <= depth:
        check_limit()
        getattr(activate(container, 'SQLQueue', **activate_kw),
                method_id)(*method_args, **method_kw)
      del recurse_stack[depth:]
    try:
      recurse(self, 0)
    except StopIteration:
      activate_kw['group_method_id'] = kw['group_id'] = '' # no grouping
      activate_kw['priority'] = 1 + activate_kw.get('priority', 1)
      activate(self, 'SQLQueue', **activate_kw)._recurseCallMethod(
        method_id, method_args, method_kw, restricted=restricted, **kw)

  security.declarePublic('recurseCallMethod')
  def recurseCallMethod(self, method_id, *args, **kw):
    """Restricted version of _recurseCallMethod"""
    if method_id[0] == '_':
        raise AccessControl_Unauthorized(method_id)
    return self._recurseCallMethod(method_id, restricted=True, *args, **kw)

OFS_HANDLER = 0
BTREE_HANDLER = 1
HBTREE_HANDLER = 2

InitializeClass(FolderMixIn)

class Folder(CopyContainer, CMFBTreeFolder, CMFHBTreeFolder, Base, FolderMixIn):
  """
  A Folder is a subclass of Base but not of XMLObject.
  Folders are not considered as documents and are therefore
  not synchronisable.

  ERP5 folders are implemented as CMFBTreeFolder objects
  and can store up to a million documents on a standard
  computer.
  ERP5 folders will eventually use in the near future the
  AdaptableStorage implementation in order to reach performances
  of 10 or 100 millions of documents in a single folder.

  ERP5 folders include an automatic id generation feature
  which allows user not to define an id when they create
  a new document in a folder.

  ERP5 folders use the ZSQLCatalog to search for objects
  or display content.

  An ERP5 Binder document class will eventually be defined
  in order to implement a binder of documents which can itself
  be categorized.
  """

  meta_type = 'ERP5 Folder'
  portal_type = 'Folder'
  add_permission = Permissions.AddPortalContent

  # Overload _properties define in OFS/Folder
  # _properties=({'id':'title', 'type': 'string','mode':'wd'},)
  # because it conflicts with title accessor generation
  _properties=()

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  manage_options = ( CMFBTreeFolder.manage_options +
                     Historical.manage_options +
                     CMFCatalogAware.manage_options
                   )
  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Folder
                    , PropertySheet.CategoryCore
                    )

  # Class inheritance fixes
  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  edit = Base.edit
  security.declareProtected( Permissions.ModifyPortalContent, '_edit' )
  _edit = Base._edit
  security.declareProtected( Permissions.ModifyPortalContent, 'setTitle' )
  setTitle = Base.setTitle
  security.declareProtected( Permissions.AccessContentsInformation, 'title_or_id' )
  title_or_id = Base.title_or_id
  security.declareProtected( Permissions.AccessContentsInformation, 'Title' )
  Title = Base.Title
  _setPropValue = Base._setPropValue
  _propertyMap = Base._propertyMap # are there any others XXX ?
  PUT_factory = None
  # XXX Prevent inheritance from PortalFolderBase
  description = None

  # Per default we use BTree folder
  _folder_handler = BTREE_HANDLER

  # Overload __init__ so that we do not take into account title
  # This is required for test_23_titleIsNotDefinedByDefault
  def __init__(self, id):
    self.id = id

  security.declarePublic('newContent')
  def newContent(self, *args, **kw):
    """ Create a new content """
    # Create data structure if none present
    return FolderMixIn.newContent(self, *args, **kw)

  def isBTree(self):
    """
    Tell if we are a BTree
    """
    return self._folder_handler == BTREE_HANDLER

  def isHBTree(self):
    """
    Tell if we are a HBTree
    """
    return self._folder_handler == HBTREE_HANDLER

  security.declareProtected( Permissions.ManagePortal, 'migrateToHBTree' )
  def migrateToHBTree(self, migration_generate_id_method=None, new_generate_id_method='_generatePerDayId', REQUEST=None):
    """
    Function to migrate from a BTree folder to HBTree folder.
    It will first call setId on all folder objects to have right id
    to be used with an hbtreefolder.
    Then it will migrate foder from btree to hbtree.
    """
    BUNDLE_COUNT = 10

    # if folder is already migrated or migration process is in progress
    # do not do anything beside logging
    if getattr(self, migration_process_lock, None) is not None \
       or self.isHBTree():
      LOG('migrateToHBTree', WARNING,
        'Folder %s already migrated'%(self.getPath(),))
      return
    # lock folder migration early
    setattr(self, migration_process_lock, 1)

    # we may want to change all objects ids before migrating to new folder type
    # set new id generator here so that object created while migration
    # got a right id
    if new_generate_id_method is not None:
      self.setIdGenerator(new_generate_id_method)
    if migration_generate_id_method not in (None, ''):
      tag = "%s/%s/migrate" %(self.getId(),migration_generate_id_method)
      id_list  = list(self.objectIds())
      # set new id by bundle
      for x in xrange(len(self) / BUNDLE_COUNT):
        self.activate(activity="SQLQueue", tag=tag).ERP5Site_setNewIdPerBundle(
          self.getPath(),
          id_list[x*BUNDLE_COUNT:(x+1)*BUNDLE_COUNT],
          migration_generate_id_method, tag)

      remaining_id_count = len(self) % BUNDLE_COUNT
      if remaining_id_count:
        self.activate(activity="SQLQueue", tag=tag).ERP5Site_setNewIdPerBundle(
          self.getPath(),
          id_list[-remaining_id_count:],
          migration_generate_id_method, tag)
    else:
      tag = 'nothing'
    # copy from btree to hbtree
    self.activate(activity="SQLQueue", after_tag=tag)._launchCopyObjectToHBTree(tag)

    if REQUEST is not None:
      psm = translateString('Migration to HBTree is running.')
      ret_url = '%s/%s?portal_status_message=%s' % \
                (self.absolute_url(),
                 REQUEST.get('form_id', 'view'), psm)
      return REQUEST.RESPONSE.redirect( ret_url )

  def _finishCopyObjectToHBTree(self):
    """
    Remove remaining attributes from previous btree
    and migration
    """
    for attr in "_tree", "_mt_index", migration_process_lock:
      try:
        delattr(self, attr)
      except AttributeError:
        pass

  def _launchCopyObjectToHBTree(self, tag):
    """
    Launch activity per bundle to move object
    from a btree to an hbtree
    """
    # migrate folder from btree to hbtree
    id_list = list(self.objectIds())
    self._folder_handler = HBTREE_HANDLER
    HBTreeFolder2Base.__init__(self, self.id)
    # launch activity per bundle to copy/paste to hbtree
    BUNDLE_COUNT = 100
    for x in xrange(len(id_list) / BUNDLE_COUNT):
      self.activate(activity="SQLQueue", tag=tag)._copyObjectToHBTree(
        id_list=id_list[x*BUNDLE_COUNT:(x+1)*BUNDLE_COUNT],)

    remaining_id_count = len(id_list) % BUNDLE_COUNT
    if remaining_id_count:
      self.activate(activity="SQLQueue", tag=tag)._copyObjectToHBTree(
        id_list=id_list[-remaining_id_count:],)
    # remove uneeded attribute
    self.activate(activity="SQLQueue", after_tag=tag)._finishCopyObjectToHBTree()

  def _copyObjectToHBTree(self, id_list=None,):
    """
    Move object from a btree container to
    a hbtree one
    """
    getOb = CMFBTreeFolder._getOb
    setOb = CMFHBTreeFolder._setOb
    for id in id_list:
      obj = getOb(self, id)
      setOb(self, id, obj)

  # Override all BTree and HBTree methods to use if/else
  # method to check wich method must be called
  # We use this method instead of plugin because it make
  # less function call and thus Folder faster
  def _initBTrees(self):
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._initBTrees(self)
    else:
      return CMFBTreeFolder._initBTrees(self)

  def hashId(self, id):
    """Return a hash of id
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.hashId(self, id)
    else:
      return CMFBTreeFolder.hashId(self, id)

  def _populateFromFolder(self, source):
    """Fill this folder with the contents of another folder.
    """
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        HBTreeFolder2Base.__init__(self, id)
      return CMFHBTreeFolder._populateFromFolder(self, source)
    else:
      if self._tree is None:
        BTreeFolder2Base.__init__(self, id)
      return CMFBTreeFolder._populateFromFolder(self, source)

  def manage_fixCount(self):
    """Calls self._fixCount() and reports the result as text.
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.manage_fixCount(self)
    else:
      return CMFBTreeFolder.manage_fixCount(self)

  def _fixCount(self):
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._fixCount(self)
    else:
      return CMFBTreeFolder._fixCount(self)

  def _fixFolderHandler(self):
    """Fixes _folder_handler if it is a string

    Bug affecting BTree folders in ERP5Type/patches/Folder.py introduced
    string value for _folder_handler, which mades methods isBTree and isHBTree
    fail.

    Returns True in case of founded and fixed error, in case
    of no error returns False.
    """
    if isinstance(self._folder_handler,str):
      delattr(self, '_folder_handler')
      return True
    return False

  def manage_cleanup(self):
    """Calls self._cleanup() and reports the result as text.
    """
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return 1
      else:
        return CMFHBTreeFolder.manage_cleanup(self)
    else:
      if self._tree is None:
        return 1
      else:
        return CMFBTreeFolder.manage_cleanup(self)

  def _cleanup(self):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return 1
      else:
        return CMFHBTreeFolder._cleanup(self)
    else:
      if self._tree is None:
        return 1
      else:
        return CMFBTreeFolder._cleanup(self)

  def _getOb(self, id, *args, **kw):
    """
    Return the named object from the folder.
    """
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        if len(args):
          return args[0]
        elif kw.has_key("default"):
          return kw["default"]
        else:
          raise KeyError, id
      return CMFHBTreeFolder._getOb(self, id, *args, **kw)
    else:
      if self._tree is None:
        if len(args):
          return args[0]
        elif kw.has_key("default"):
          return kw["default"]
        else:
          raise KeyError, id
      return CMFBTreeFolder._getOb(self, id, *args, **kw)

  def _setOb(self, id, object):
    """Store the named object in the folder.
    """
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        HBTreeFolder2Base.__init__(self, self.id)
      return CMFHBTreeFolder._setOb(self, id, object)
    else:
      if self._tree is None:
        BTreeFolder2Base.__init__(self, self.id)
      return CMFBTreeFolder._setOb(self, id, object)

  def _delOb(self, id):
    """Remove the named object from the folder.
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._delOb(self, id)
    else:
      return CMFBTreeFolder._delOb(self, id)

  def getBatchObjectListing(self, REQUEST=None):
    """Return a structure for a page template to show the list of objects.
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.getBatchObjectListing(self, REQUEST)
    else:
      return CMFBTreeFolder.getBatchObjectListing(self, REQUEST)

  def manage_object_workspace(self, ids=(), REQUEST=None):
    '''Redirects to the workspace of the first object in
    the list.'''
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.manage_object_workspace(self, ids, REQUEST)
    else:
      return CMFBTreeFolder.manage_object_workspace(self, ids, REQUEST)

  def manage_main(self, *args, **kw):
    ''' List content.'''
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.manage_main.__of__(self)(self, *args, **kw)
    else:
      return CMFBTreeFolder.manage_main.__of__(self)(self, *args, **kw)

  def tpValues(self):
    """Ensures the items don't show up in the left pane.
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.tpValues(self)
    else:
      return CMFBTreeFolder.tpValues(self)

  def objectCount(self):
    """Returns the number of items in the folder."""
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return 0
      return CMFHBTreeFolder.objectCount(self)
    else:
      if self._tree is None:
        return 0
      return CMFBTreeFolder.objectCount(self)

  def has_key(self, id):
    """Indicates whether the folder has an item by ID.
    """
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return False
      return CMFHBTreeFolder.has_key(self, id)
    else:
      if self._tree is None:
        return False
      return CMFBTreeFolder.has_key(self, id)

  def treeIds(self, base_id=None):
    """ Return a list of subtree ids
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.treeIds(self, base_id)
    else:
      return CMFBTreeFolder.treeIds(self, base_id)

  def _getTree(self, base_id):
    """ Return the tree wich has the base_id
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._getTree(self, base_id)
    else:
      return CMFBTreeFolder._getTree(self, base_id)

  def _getTreeIdList(self, htree=None):
    """ recursively build a list of btree ids
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._getTreeIdList(self, htree)
    else:
      return CMFBTreeFolder._getTreeIdList(self, htree)

  def getTreeIdList(self, htree=None):
    """ recursively build a list of btree ids
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.getTreeIdList(self, htree)
    else:
      return CMFBTreeFolder.getTreeIdList(self, htree)

  def _treeObjectValues(self, base_id=None):
    """ return object values for a given btree
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._treeObjectValues(self, base_id)
    else:
      return CMFBTreeFolder._treeObjectValues(self, base_id)

  def _treeObjectIds(self, base_id=None):
    """ return object ids for a given btree
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._treeObjectIds(self, base_id)
    else:
      return CMFBTreeFolder._treeObjectIds(self, base_id)

  def _isNotBTree(self, obj):
    """ test object is not a btree
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._isNotBTree(self, obj)
    else:
      return CMFBTreeFolder._isNotBTree(self, obj)

  def _checkObjectId(self, id):
    """ test id is not in btree id list
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._checkObjectId(self, id)
    else:
      return CMFBTreeFolder._checkObjectId(self, id)

  def objectIds(self, spec=None, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return []
      assert spec is None
      if kw.has_key("base_id"):
        return CMFHBTreeFolder.objectIds(self, base_id=kw["base_id"])
      else:
        return CMFHBTreeFolder.objectIds(self)
    else:
      if self._tree is None:
        return []
      return CMFBTreeFolder.objectIds(self, spec)

  def objectItems(self, spec=None, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      if  self._htree is None:
        return []
      assert spec is None
      if kw.has_key("base_id"):
        return CMFHBTreeFolder.objectItems(self, base_id=kw["base_id"])
      else:
        return CMFHBTreeFolder.objectItems(self)
    else:
      if  self._tree is None:
        return []
      return CMFBTreeFolder.objectItems(self, spec)

  def objectIds_d(self, t=None):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return {}
      return CMFHBTreeFolder.objectIds_d(self, t)
    else:
      if self._tree is None:
        return {}
      return CMFBTreeFolder.objectIds_d(self, t)

  def _checkId(self, id, allow_dup=0):
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder._checkId(self, id, allow_dup)
    else:
      return CMFBTreeFolder._checkId(self, id, allow_dup)

  def _setObject(self, *args, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        HBTreeFolder2Base.__init__(self, self.id)
      return CMFHBTreeFolder._setObject(self, *args, **kw)
    else:
      if self._tree is None:
        BTreeFolder2Base.__init__(self, self.id)
      return CMFBTreeFolder._setObject(self, *args, **kw)

  def get(self, id, default=None):
    """
    Return the named object from the folder.
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.get(self, id, default)
    else:
      return CMFBTreeFolder.get(self, id, default)

  def generateId(self, prefix='item', suffix='', rand_ceiling=999999999):
    """Returns an ID not used yet by this folder.

    The ID is unlikely to collide with other threads and clients.
    The IDs are sequential to optimize access to objects
    that are likely to have some relation.
    """
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.generateId(self, prefix, suffix, rand_ceiling)
    else:
      return CMFBTreeFolder.generateId(self, prefix, suffix, rand_ceiling)

  def __getattr__(self, name):
    if self._folder_handler == HBTREE_HANDLER:
      return CMFHBTreeFolder.__getattr__(self, name)
    else:
      if self._tree is None:
        raise AttributeError, name
      return CMFBTreeFolder.__getattr__(self, name)

  def __len__(self):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return 0
      return CMFHBTreeFolder.__len__(self)
    else:
      if self._tree is None:
        return 0
      return CMFBTreeFolder.__len__(self)

  def keys(self, *args, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return []
      return CMFHBTreeFolder.keys(self, *args, **kw)
    else:
      if self._tree is None:
        return []
      return CMFBTreeFolder.keys(self, *args, **kw)

  def values(self, *args, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return []
      return CMFHBTreeFolder.values(self, *args, **kw)
    else:
      if self._tree is None:
        return []
      return CMFBTreeFolder.values(self, *args, **kw)

  def items(self, *args, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return []
      return CMFHBTreeFolder.items(self, *args, **kw)
    else:
      if self._tree is None:
        return []
      return CMFBTreeFolder.items(self, *args, **kw)

  def iteritems(self, *args, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      result = CMFHBTreeFolder._htree_iteritems(self, *args, **kw)
    else:
      if self._tree is None:
        return ()
      result = self._tree.iteritems(*args, **kw)
    return NullIter(((x, y.__of__(self)) for x, y in result))

  def hasObject(self, id):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return False
      return CMFHBTreeFolder.hasObject(self, id)
    else:
      if self._tree is None:
        return False
      return CMFBTreeFolder.hasObject(self, id)

  # Work around for the performance regression introduced in Zope 2.12.23.
  # Otherwise, we use superclass' __contains__ implementation, which uses
  # objectIds, which is inefficient in HBTreeFolder2 to lookup a single key.
  __contains__ = hasObject

  # Override Zope default by folder id generation
  def _get_id(self, id):
    if self._getOb(id, None) is None :
      return id
    return self.generateNewId()

  #security.declareProtected( Permissions.DeletePortalContent, 'manage_delObjects' )
  #manage_delObjects = CopyContainer.manage_delObjects

  # Implementation
  hasContent = hasObject

  security.declareProtected( Permissions.ModifyPortalContent, 'exportAll' )
  def exportAll(self,dir=None):
    """
    Allows to export all object inside a particular folder, one by one
    """
    folder_id = self.getId()
    if dir != None:
      for id in self.objectIds():
        f = os.path.join(dir, '%s___%s.zexp' % (folder_id,id))
        ob = self._getOb(id)
        ob._p_jar.exportFile(ob._p_oid,f)
      transaction.commit()

  security.declareProtected( Permissions.ModifyPortalContent, 'recursiveApply')
  def recursiveApply(self, filter=dummyFilter, method=None,
                    test_after=dummyTestAfter, include=1, REQUEST=None, **kw):
    """
      Apply a method to self and to all children

      filter      --    only instances which return 1 when applied filter
                        are considered

      method      --    the method to apply to acceptable instances

      test_after  --    test to apply after calling method in order to search
                        for inconsistencies

      include     --    if set to 1 (default), apply method to self


      REQUEST     --    the http REQUEST (if needed)

      **kw        --    optional parameters passed to method
    """
    update_list = []
    #LOG('Folder, recursiveApply ',0,"first one self.path: %s" % self.getPath())

    # Only apply method to self if filter is to 1 and filter returns 1
    if include==1 and filter(object=self.getObject(),REQUEST=REQUEST):
      method_message = method(object=self.getObject(),REQUEST=REQUEST, **kw)
      if type(method_message) is type([]):
        update_list += method_message
      update_list += test_after(object=self.getObject(),REQUEST=REQUEST)

    for o in self.objectValues(): # contentValues sometimes fail in BTreeFolder
      # Test on each sub object if method should be applied
      if filter(object=o,REQUEST=REQUEST):
        method_message = method(object=o,REQUEST=REQUEST, **kw)
        if type(method_message) is type([]):
          update_list += method_message
        update_list += test_after(o,REQUEST=REQUEST)
      # And commit subtransaction
      #transaction.savepoint(optimistic=True)
      transaction.commit() # we may use commit(1) some day XXX
      # Recursively call recursiveApply if o has a recursiveApply method (not acquired)
      obase = aq_base(o)
      if hasattr(obase, 'recursiveApply'):
        #LOG('Found recursiveApply', 0, o.absolute_url())
        update_list += o.recursiveApply(filter=filter, \
                              method=method, test_after=test_after,REQUEST=REQUEST,include=0,**kw)

    return update_list

  security.declareProtected( Permissions.ModifyPortalContent, 'updateAll' )
  def updateAll(self, filter=None, method=None, test_after=None, request=None, include=1,**kw):
    """
    update all objects inside this particular folder wich
    returns not None to the test.

    filter have to be a method with one parameter (the object)
    wich returns None if we must not update the object

    test_after have to be a method with one parameter (the object)
    wich returns a string

    method is the update method with also one parameter

    """
    update_list = []
    #LOG('Folder, updateAll ',0,"first one self.path: %s" % self.getPath())

    if include==1 and filter(object=self.getObject(),request=request):
      method_message = method(object=self.getObject(),request=request)
      if type(method_message) is type([]):
        update_list += method_message
      update_list += test_after(object=self.getObject(),request=request)

    for o in self.objectValues():
      # Test if we must apply the upgrade
      if filter(object=o,request=request):
        method_message = method(object=o,request=request)
        if type(method_message) is type([]):
          update_list += method_message
        update_list += test_after(object=o,request=request)
      #for object in o.objectValues():
        #LOG('Folder, updateAll ',0,"object.id: %s" % object.id)
      obase = aq_base(o)
      transaction.commit()
      if hasattr(obase, 'updateAll'):
        update_list += o.updateAll(filter=filter, \
                              method=method, test_after=test_after,request=request,include=0,**kw)

    return update_list

  security.declareProtected( Permissions.ModifyPortalContent, 'upgradeObjectClass' )
  def upgradeObjectClass(self, test_before, from_class, to_class, test_after,
                               test_only=0):
    """
    Upgrade the class of all objects inside this particular folder:
      test_before and test_after have to be a method with one parameter.

      from_class and to_class can be classes (o.__class___) or strings like:
        'Products.ERP5Type.Document.Folder.Folder'

    XXX Some comments by Seb:
    - it is not designed to work for modules with thousands of objects,
      so it totally unusable when you have millions of objects
    - it is totally unsafe. There is even such code inside :
        self.manage_delObjects(id of original object)
        commit()
        self._setObject(new object instance)
      So it is possible to definitely loose data.
    - There is no proof that upgrade is really working. With such a
      dangerous operation, it would be much more safer to have a proof,
      something like the "fix point" after doing a synchronization. Such
      checking should even be done before doing commit (like it might
      be possible to export objects in the xml format used for exports
      before and after, and run a diff).

    """
    #LOG("upgradeObjectClass: folder ", 0, self.id)
    test_list = []
    def getClassFromString(a_klass):
      from_module = '.'.join(a_klass.split('.')[:-1])
      real_klass = a_klass.split('.')[-1]
      # XXX It is possible that API Change for Python 2.6.
      mod = __import__(from_module, globals(), locals(),  [real_klass])
      return getattr(mod, real_klass)

    if isinstance(from_class, type('')):
      from_class = getClassFromString(from_class)

    if isinstance(to_class, type('')):
      to_class = getClassFromString(to_class)

    for o in self.listFolderContents():
      # Make sure this sub object is not the same as object
      if o.getPhysicalPath() != self.getPhysicalPath():
        id = o.getId()
        obase = aq_base(o)
        # Check if the subobject have to also be upgraded
        if hasattr(obase,'upgradeObjectClass'):
          test_list += o.upgradeObjectClass(test_before=test_before, \
                          from_class=from_class, to_class=to_class,
                          test_after=test_after, test_only=test_only)

        # Test if we must apply the upgrade
        if test_before(o) is not None:
          LOG("upgradeObjectClass: id ", 0, id)
          klass = obase.__class__
          LOG("upgradeObjectClass: klass ", 0 ,str(klass))
          LOG("upgradeObjectClass: from_class ", 0 ,str(from_class))
          if klass == from_class and not test_only:
            try:
              newob = to_class(obase.id)
              newob.id = obase.id # This line activates obase.
            except AttributeError:
              newob = to_class(id)
              newob.id = id
            keys = obase.__dict__.keys()
            for k in keys:
              if k not in ('id', 'meta_type', '__class__'):
                setattr(newob,k,obase.__dict__[k])

            self.manage_delObjects(id)
            LOG("upgradeObjectClass: ",0,"add new object: %s" % str(newob.id))
            transaction.commit() # XXX this commit should be after _setObject
            LOG("upgradeObjectClass: ",0,"newob.__class__: %s" % str(newob.__class__))
            self._setObject(id, newob)
            object_to_test = self._getOb(id)
            test_list += test_after(object_to_test)

          if klass == from_class and test_only:
            test_list += test_after(o)

    return test_list


  # Catalog related
  security.declarePublic( 'reindexObject' )
  def reindexObject(self, *args, **kw):
    """Fixes the hierarchy structure (use of Base class)
    """
    return Base.reindexObject(self, *args, **kw)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'reindexObjectSecurity')
  def reindexObjectSecurity(self, *args, **kw):
    """
        Reindex security-related indexes on the object
    """
    # In ERP5, simply reindex all objects, recursively by default.
    reindex = self._getTypeBasedMethod('reindexObjectSecurity',
                                       'recursiveReindexObject')
    reindex(*args, **kw)

  security.declarePublic( 'recursiveReindexObject' )
  def recursiveReindexObject(self, activate_kw=None, **kw):
    """Recursively indexes the content of self.
    """
    if self.isIndexable:
      if not activate_kw and self.objectCount() > REINDEX_SPLIT_COUNT:
        # If the number of objects to reindex is too high
        # we should try to split reindexing in order to be more efficient
        # NOTE: this heuristic will fail for example with orders which
        # contain > REINDEX_SPLIT_COUNT order lines.
        # It will be less efficient in this case. We also do not
        # use this heuristic whenever activate_kw is defined
        self._reindexObject(**kw)
        # XXX-JPS: Here, we could invoke Folder_reindexAll instead, like this:
        #   self.Folder_reindexAll()
        #   return
        # this shows that both methods should be merged.
        for c in self.objectValues():
          if getattr(aq_base(c),
                    'recursiveReindexObject', None) is not None:
            c.recursiveReindexObject(**kw)
        return

      if activate_kw is None:
        activate_kw = {}

      reindex_kw = self.getDefaultReindexParameterDict()
      if reindex_kw is not None:
        reindex_kw = reindex_kw.copy()
        reindex_activate_kw = reindex_kw.pop('activate_kw', None) or {}
        reindex_activate_kw.update(activate_kw)
        reindex_kw.update(kw)
        kw = reindex_kw
        activate_kw = reindex_activate_kw

      group_id_list  = []
      if kw.get("group_id", "") not in ('', None):
        group_id_list.append(kw.get("group_id", ""))
      if kw.get("sql_catalog_id", "") not in ('', None):
        group_id_list.append(kw.get("sql_catalog_id", ""))
      group_id = ' '.join(group_id_list)

      self.activate(group_method_id='portal_catalog/catalogObjectList',
                    expand_method_id='getIndexableChildValueList',
                    alternate_method_id='alternateReindexObject',
                    group_id=group_id,
                    serialization_tag=self.getRootDocumentPath(),
                    **activate_kw).recursiveImmediateReindexObject(**kw)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getIndexableChildValueList' )
  def getIndexableChildValueList(self):
    """
      Get indexable childen recursively.
    """
    value_list = []
    if self.isIndexable:
      value_list.append(self)
      for c in self.objectValues():
        if getattr(aq_base(c), 'getIndexableChildValueList', None) is not None:
          value_list.extend(c.getIndexableChildValueList())
    return value_list

  security.declarePublic( 'recursiveImmediateReindexObject' )
  def recursiveImmediateReindexObject(self, **kw):
      """
        Applies immediateReindexObject recursively
      """
      # Reindex self
      root_indexable = int(getattr(self.getPortalObject(),'isIndexable',1))
      if self.isIndexable and root_indexable:
        self.immediateReindexObject(**kw)
      # Reindex contents
      for c in self.objectValues():
        if getattr(aq_base(c),
                   'recursiveImmediateReindexObject', None) is not None:
          c.recursiveImmediateReindexObject(**kw)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'recursiveMoveObject' )
  def recursiveMoveObject(self):
    """
      Called when the base of a hierarchy is renamed
    """
    # Reindex self
    if self.isIndexable:
      self.moveObject()
    # Reindex contents
    for c in self.objectValues():
      if getattr(aq_base(c), 'recursiveMoveObject', None) is not None:
        c.recursiveMoveObject()

  # Special Relation keyword : 'content' and 'container'
  security.declareProtected( Permissions.AccessContentsInformation,
                             '_getCategoryMembershipList' )
  def _getCategoryMembershipList(self, category,
                                 spec=(), filter=None, portal_type=(), base=0,
                                 keep_default=None, checked_permission=None):
    if category == 'content':
      content_list = self.searchFolder(portal_type=spec)
      return map(lambda x: x.relative_url, content_list)
    else:
      return Base.getCategoryMembershipList(self, category,
          spec=spec, filter=filter, portal_type=portal_type, base=base)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'checkConsistency')
  def checkConsistency(self, fixit=False, filter=None, **kw):
    """
    Check the consistency of this object, then
    check recursively the consistency of every sub object.
    """
    error_list = []
    # Fix BTree
    if fixit:
      btree_ok = self._cleanup()
      if not btree_ok:
        # We must commit if we want to keep on recursing
        transaction.savepoint(optimistic=True)
        error_list += [(self.getRelativeUrl(), 'BTree Inconsistency',
                       199, '(fixed)')]
    # Call superclass
    error_list += Base.checkConsistency(self, fixit=fixit, filter=filter, **kw)
    # We must commit before listing folder contents
    # in case we erased some data
    if fixit:
      transaction.savepoint(optimistic=True)
    # Then check the consistency on all sub objects
    for obj in self.contentValues():
      if obj.providesIConstraint():
        # it is not possible to checkConsistency of Constraint itself, as method
        # of this name implement consistency checking on object
        continue
      if fixit:
        extra_errors = obj.fixConsistency(filter=filter, **kw)
      else:
        extra_errors = obj.checkConsistency(filter=filter, **kw)
      if len(extra_errors) > 0:
        error_list += extra_errors
    # We should also return an error if any
    return error_list

  security.declareProtected(Permissions.AccessContentsInformation, 'asXML')
  def asXML(self, omit_xml_declaration=True, root=None):
    """
        Generate an xml text corresponding to the content of this object
    """
    return Folder_asXML(self, omit_xml_declaration=omit_xml_declaration, root=root)

  # Optimized Menu System
  security.declarePublic('getVisibleAllowedContentTypeList')
  def getVisibleAllowedContentTypeList(self):
    """
      List portal_types' names wich can be added in this folder / object.

      This function is *much* similar to allowedContentTypes, except it does
      not returns portal types but their ids and filter out those listed as
      hidden content types. It allows to be much faster when only the type id
      is needed.
    """
    portal = self.getPortalObject()

    # If the user can manage the portal, do not hide any content types.
    sm = getSecurityManager()
    if sm.checkPermission(Permissions.ManagePortal, portal):
      return [ti.id for ti in self.allowedContentTypes()]

    hidden_type_list = portal.portal_types.getTypeInfo(self)\
                                              .getTypeHiddenContentTypeList()
    return [ ti.id for ti in self.allowedContentTypes()
               if ti.id not in hidden_type_list ]

  # Multiple Inheritance Priority Resolution
  _setProperty = Base._setProperty
  setProperty = Base.setProperty
  getProperty = Base.getProperty
  hasProperty = Base.hasProperty
  view = Base.view

  # Aliases
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getObjectIds')
  def getObjectIds(self, *args, **kw):
    return self.objectIds(*args, **kw)

  # Overloading
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getParentSQLExpression')
  def getParentSQLExpression(self, table='catalog', strict_membership=0):
    """
      Builds an SQL expression to search children and subchildren
    """
    if strict_membership:
      return Base.getParentSQLExpression(self,
                                         table=table,
                                         strict_membership=strict_membership)
    result = "%s.parent_uid = %s" % (table, self.getUid())
    for o in self.objectValues():
      if hasattr(aq_base(o), 'objectValues'):
        # Do not consider non folder objects
        result = "%s OR %s" % ( result,
                                o.getParentSQLExpression(table=table,
                                          strict_membership=strict_membership))
    return "( %s )" % result


  def mergeContent(self,from_object=None,to_object=None, delete=1,**kw):
    """
    This method will merge two objects.

    When we have to different objects wich represent the same content, we
    may want to merge them. In this case, we want to be sure to report

    """
    if from_object is None or to_object is None:
      return

    from_object_related_object_list = self.portal_categories\
                                          .getRelatedValueList(from_object)
    to_object_url = to_object.getRelativeUrl()
    from_object_url = from_object.getRelativeUrl()
    corrected_list = []
    for object in from_object_related_object_list:
      #LOG('Folder.mergeContent, working on object:',0,object)
      new_category_list = []
      found = 0
      for category in object.getCategoryList(): # so ('destination/person/1',...)
        #LOG('Folder.mergeContent, working on category:',0,category)
        linked_object_url = '/'.join(category.split('/')[1:])
        if linked_object_url == from_object_url:
          base_category = category.split('/')[0]
          found = 1
          new_category_list.append(base_category + '/' + to_object_url)
        else:
          new_category_list.append(category)
      if found:
        corrected_list.append(object)
        object.setCategoryList(new_category_list)
        object.immediateReindexObject()
    if delete:
      if len(from_object.portal_categories.getRelatedValueList(from_object))==0:
        parent = from_object.getParentValue()
        parent.manage_delObjects(from_object.getId())
    return corrected_list

  security.declareProtected( Permissions.AccessContentsInformation,
                             'objectValues' )
  def objectValues(self, spec=None, meta_type=None, portal_type=None,
                   sort_on=None, sort_order=None, checked_permission=None,
                   **kw):
    # Returns list of objects contained in this folder.
    #  (no docstring to prevent publishing)
    if meta_type is not None:
      spec = meta_type
    if self._folder_handler == BTREE_HANDLER:
      if self._tree is None:
        return []
      object_list = CMFBTreeFolder.objectValues(self, spec=spec)
    elif self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return []
      assert spec is None
      if 'base_id' in kw:
        object_list = CMFHBTreeFolder.objectValues(self, base_id=kw['base_id'])
      else:
        object_list = CMFHBTreeFolder.objectValues(self)
    else:
      object_list = map(self._getOb, self.objectIds(spec))
    if portal_type is not None:
      if isinstance(portal_type, str):
        portal_type = (portal_type,)
      object_list = filter(lambda x: x.getPortalType() in portal_type,
                           object_list)
    if checked_permission is not None:
      checkPermission = getSecurityManager().checkPermission
      object_list = [o for o in object_list
                       if checkPermission(checked_permission, o)]
    return sortValueList(object_list, sort_on, sort_order, **kw)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'contentValues' )
  def contentValues(self, *args, **kw):
    # Returns a list of documents contained in this folder.
    # ( no docstring to prevent publishing )
    portal_type_id_list = self._getTypesTool().listContentTypes()
    filter_kw = kw.pop('filter', None) or {}
    portal_type = kw.pop('portal_type', None)
    if 'portal_type' in filter_kw:
      portal_type = filter_kw.pop('portal_type')
    if portal_type is None:
      kw['portal_type'] = portal_type_id_list
    else:
      if isinstance(portal_type, str):
        portal_type = portal_type,
      kw['portal_type'] = [x for x in portal_type if x in portal_type_id_list]
    object_list = self.objectValues(*args, **kw)
    if filter_kw:
      object_list = filter(ContentFilter(**filter_kw), object_list)
    return object_list

  # Override security declaration of CMFCore/PortalFolder (used by CMFBTreeFolder)
  security.declareProtected(Permissions.ModifyPortalContent,'setDescription')

  # XXX Why this one doesn't work in CopySupport ?
  security.declareProtected( Permissions.AccessContentsInformation,
                             'manage_copyObjects' )
  security.declareProtected( Permissions.AddPortalContent,
                             'manage_pasteObjects' )

  # Template Management
  security.declareProtected(Permissions.View, 'getDocumentTemplateList')
  def getDocumentTemplateList(self) :
    """
      Returns the list of allowed templates for this folder
      by calling the preference tool
    """
    return self.getPortalObject().portal_preferences\
                              .getDocumentTemplateList(self)

  security.declareProtected(Permissions.ModifyPortalContent, 'makeTemplate')
  def makeTemplate(self):
    """
      Make document behave as a template.
      A template is no longer indexable
    """
    Base.makeTemplate(self)
    for o in self.objectValues():
      if getattr(aq_base(o), 'makeTemplate', None) is not None:
        o.makeTemplate()

  security.declareProtected( Permissions.ModifyPortalContent,
                             'makeTemplateInstance' )
  def makeTemplateInstance(self):
    """
      Make document behave as standard document (indexable)
    """
    Base.makeTemplateInstance(self)
    for o in self.objectValues():
      if getattr(aq_base(o), 'makeTemplateInstance', None) is not None:
        o.makeTemplateInstance()

  def _delObject(self, id, dp=1, suppress_events=True):
    """
      _delObject is redefined here in order to make sure
      we do not do silent except while we remove objects
      from catalog

      Note that we always suppress / do not use events.
    """
    object = self._getOb(id)
    object.manage_beforeDelete(object, self)
    self._delOb(id)

  security.declareProtected(Permissions.ManagePortal, 'callMethodOnObjectList')
  def callMethodOnObjectList(self, object_path_list, method_id, *args, **kw):
    """
    Very useful if we want to activate the call of a method
    on many objects at a time. Like this we could prevent creating
    too many activities at a time, and we may have only the path
    """
    result_list = []
    traverse = self.getPortalObject().unrestrictedTraverse
    for object_path in object_path_list:
      result = getattr(traverse(object_path), method_id)(*args, **kw)
      if type(result) in (list, tuple):
        result_list += result
    return result_list

  def _verifyObjectPaste(self, object, validate_src=1):
    # To paste in an ERP5Type folder, we need to check 'Add permission'
    # that might be defined on the sub object type information.
    pt = self.getPortalObject().portal_types
    subobject_type = pt.getTypeInfo(object)
    if subobject_type is not None:
      sm = getSecurityManager()
      parent = aq_parent(aq_inner(object))

      # check allowed content types
      type_name = subobject_type.getId()
      myType = pt.getTypeInfo(self)
      if myType is not None and not myType.allowType(type_name):
        raise ValueError('Disallowed subobject type: %s' % type_name)

      # Check Add permission (ERPType addition)
      add_permission = getattr(aq_base(subobject_type), 'permission', '')
      if add_permission:
        if not sm.checkPermission(add_permission, self):
          raise AccessControl_Unauthorized, add_permission

      # handle validate_src
      if validate_src:
        if not sm.validate(None, parent, None, object):
          raise AccessControl_Unauthorized, object.getId()
      if validate_src > 1:
        if not sm.checkPermission(Permissions.DeleteObjects, parent):
          raise AccessControl_Unauthorized
      # so far, everything OK
      return

    # if we haven't been able to validate, pass through to parent class
    Folder.inheritedAttribute(
          '_verifyObjectPaste')(self, object, validate_src)

  security.declarePublic('getIconURL')
  def getIconURL(self):
    """ Get the absolute URL of the icon for the object.
        Patched, as ERP5 Type does not provide getExprContext which is used in
        CMF 2.2
    """
    icon = 'misc_/OFSP/dtmldoc.gif'
    ti = self.getTypeInfo()
    url = self.getPortalObject().portal_url()
    if ti is not None:
      try:
        icon = ti.getTypeIcon()
      except AttributeError:
        # do not fail in case of accessor is not available
        pass
    return '%s/%s' % (url, icon)

# We browse all used class from btree and hbtree and set not implemented
# class if one method defined on a class is not defined on other, thus if
# new method appears in one class if will raise in the other one
class NotImplementedClass(object):
  def __init__(self, method_id):
    self.__name__ = method_id

  def __call__(self, *args, **kw):
    raise NotImplementedError, str(self.__name__)

for source_klass, destination_klass in \
        (
         # Check method on HBTree but not on BTree
         (HBTreeFolder2Base, BTreeFolder2Base),
         (HBTreeFolder2, BTreeFolder2),
         (CMFHBTreeFolder, CMFBTreeFolder),
         # Check method on BTree but not on HBTree
         (BTreeFolder2Base, HBTreeFolder2Base),
         (BTreeFolder2, HBTreeFolder2),
         (CMFBTreeFolder, CMFHBTreeFolder),
        ):
  # It is better to avoid methods starting with ___, because they have
  # special meanings in Python or Zope, and lead to strange errors
  # when set to an unexpected value. In fact, __implemented__ should not
  # be set this way, otherwise Zope crashes.
  for method_id in source_klass.__dict__:
    if (method_id[:2] != '__' and method_id[:7] != '_htree_' and
        callable(getattr(source_klass, method_id)) and
        not hasattr(destination_klass, method_id)):
      setattr(destination_klass, method_id, NotImplementedClass(method_id))
      # Zope 2.7 required to have methodId__roles__ defined
      # to know the security ot the method
      setattr(destination_klass, method_id+'__roles__', None)
