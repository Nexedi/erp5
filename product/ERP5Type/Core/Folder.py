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
from functools import wraps
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.ZopeGuards import NullIter, guarded_getattr
from Acquisition import aq_base, aq_parent, aq_inner
from BTrees.Length import Length
from OFS.Folder import Folder as OFSFolder
from OFS.ObjectManager import ObjectManager, checkValidId
from zExceptions import BadRequest
from OFS.History import Historical
import ExtensionClass
from Persistence import Persistent
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.PortalFolder import ContentFilter
from Products.ERP5Type.Base import Base
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
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
from urlparse import urlparse
from Products.ERP5Type.Message import translateString
from ZODB.POSException import ConflictError

# Dummy Functions for update / upgrade
def dummyFilter(object,REQUEST=None):
  return 1

def dummyTestAfter(object,REQUEST=None):
  return []

class ExceptionRaised(object):
  raised = False

  def __nonzero__(self):
    return self.raised

  def __call__(self, func):
    def wrapper(*args, **kw):
      try:
        return func(*args, **kw)
      except:
        self.raised = True
        raise
    return wraps(func)(wrapper)

# Above this many subobjects, migrate _count from Length to FragmentedLength
# to accomodate concurrent accesses.
FRAGMENTED_LENGTH_THRESHOLD = 1000
class FragmentedLength(Persistent):
  """
  Drop-in replacement for BTrees.Length, which splits storage by zope node.
  The intent is that per-node conflicts should be roughly constant, but adding
  more nodes should not increase overall conflict rate.

  Inherit from Persistent in order to be able to resolve our own conflicts
  (first time a node touches an instance of this class), which should be a rare
  event per-instance.
  Contain BTrees.Length instances for intra-node conflict resolution
  (inter-threads).
  """
  def __init__(self, legacy=None):
    self._map = {}
    if legacy is not None:
      # Key does not matter as long as it is independent from the node
      # constructing this instance.
      self._map[None] = legacy

  def set(self, new):
    self._map.clear()
    self.change(new)

  def change(self, delta):
    try:
      self._map[getCurrentNode()].change(delta)
    except KeyError:
      self._map[getCurrentNode()] = Length(delta)
      # _map is mutable, notify persistence that we have to be serialised.
      self._p_changed = 1

  def __call__(self):
    return sum(x() for x in self._map.values())

  @staticmethod
  def _p_resolveConflict(old_state, current_state, my_state):
    # Minimal implementation for sanity: only handle addition of one by "me" as
    # long as current_state does not contain the same key. Anything else is a
    # conflict.
    try:
      my_added_key, = set(my_state['_map']).difference(old_state['_map'])
    except ValueError:
      raise ConflictError
    if my_added_key in current_state:
      raise ConflictError
    current_state['_map'][my_added_key] = my_state['_map'][my_added_key]
    return current_state

class FolderMixIn(ExtensionClass.Base):
  """A mixin class for folder operations, add content, delete content etc.
  """
  # flag to hold the status of migration for this folder
  _migration_in_progress = False

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
    elif not temp_object:
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
      container._setObject(new_id, new_instance.aq_base)
    elif self._migration_in_progress:
      raise RuntimeError("Folder is running migration to HBTree")
    else:
      # make sure another zope hasn't started to migrate to HBTree
      connection = self._p_jar
      connection is None or connection.readCurrent(self)

    return new_instance

  security.declareProtected(
            Permissions.DeletePortalContent, 'deleteContent')
  def deleteContent(self, id):
    """ delete items in this folder.
      `id` can be a list or a string.
    """
    if self._migration_in_progress:
      raise RuntimeError("Folder is running migration to HBTree")
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
    new_id = "%s-%s" %(getCurrentNode().replace("-", "_"),
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
    current_node = getCurrentNode()
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
    current_node = getCurrentNode()
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
    hook_raised = ExceptionRaised()
    my_getattr = guarded_getattr if restricted else getattr
    activate = self.getPortalObject().portal_activities.activateObject
    validate = restricted and getSecurityManager().validate
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
      # We are called by user (and not in a subsequent activity).
      # Complete activate_kw, without mutating received value.
      activate_kw = self.getDefaultActivateParameterDict.im_func(None)
      activate_kw.update(kw.get('activate_kw', ()))
      activate_kw.setdefault('active_process', None)
      activate_kw.setdefault('activity', 'SQLQueue')
      cost = activate_kw.setdefault('group_method_cost', .034) # 30 objects
      if cost != 1:
        activate_kw.setdefault('group_method_id', None) # dummy group method
      kw['activate_kw'] = activate_kw
    else:
      activate_kw = kw['activate_kw']
    min_depth = kw.get('min_depth', 0)
    max_depth = kw.get('max_depth', 0)
    get_activate_kw_method_id = kw.get('get_activate_kw_method_id')
    if get_activate_kw_method_id is None:
      getActivateKw = lambda document, activate_kw: activate_kw
      recurse_activate_kw = activate_kw
    else:
      getActivateKw = hook_raised(my_getattr(self, get_activate_kw_method_id))
      # Isolate caller-accessible mutable activate_kw from the on we need to
      # re-invoke ourselves. Doing it once only should be sufficient (and saves a
      # dict copy on each iteration) as all the values we care about (set above
      # in this script) are immutable. Anything else is already under the control
      # of caller, either via arguments or via default activate parameter dict.
      recurse_activate_kw = activate_kw.copy()
    skip_method_id = kw.get('skip_method_id')
    if skip_method_id is None:
      skip = lambda document: False
    else:
      skip = hook_raised(my_getattr(self, skip_method_id))
    def recurse(container, depth):
      if getattr(aq_base(container), 'getPhysicalPath', None) is None or skip(container):
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
        getattr(activate(container, **getActivateKw(container, recurse_activate_kw)),
                method_id)(*method_args, **method_kw)
      del recurse_stack[depth:]
    try:
      recurse(self, 0)
    except StopIteration:
      if hook_raised:
        raise
      reactivate_kw = activate_kw.copy()
      reactivate_kw['group_method_id'] = reactivate_kw['group_id'] = '' # no grouping
      reactivate_kw['activity'] = 'SQLQueue'
      activate(self, **reactivate_kw)._recurseCallMethod(
        method_id, method_args, method_kw, restricted=restricted, **kw)

  security.declarePublic('recurseCallMethod')
  def recurseCallMethod(self, method_id, *args, **kw):
    """Restricted version of _recurseCallMethod"""
    if method_id[0] == '_':
        raise AccessControl_Unauthorized(method_id)
    return self._recurseCallMethod(method_id, restricted=True, *args, **kw)

  security.declarePublic('isURLAncestorOf')
  def isURLAncestorOf(self, given_url):
    """
      This method returns True if the given_url is child of the url of
      the document that the method is called on, False otherwise.

      Note that the method compares the urls as strings and does
      not access any document in given path,
      hence it does not compute the inner acquisition path.
    """
    document_url = self.absolute_url()
    parsed_given_url = urlparse(given_url)
    parsed_document_url = urlparse(document_url)
    # XXX note that the following check:
    # - does not support relative urls
    # - does not canonicalize domain name, e.g.
    #   http://foo:80/erp5, http://foo/erp5 and http://foo:www/erp5
    #   will not match.
    return parsed_given_url.scheme == parsed_document_url.scheme and \
        parsed_given_url.netloc == parsed_document_url.netloc and \
        (parsed_given_url.path + '/').startswith((parsed_document_url.path + '/'))

InitializeClass(FolderMixIn)

class OFSFolder2(OFSFolder):
  """
  Make OFSFolder behave more consistently with (H)BTreeFolder2, especially
  exception-wise.
  """
  def _getOb(self, *args, **kw):
    try:
      return OFSFolder._getOb(self, *args, **kw)
    except AttributeError as exc:
      raise KeyError(exc.args)

OFS_HANDLER = 0
BTREE_HANDLER = 1
HBTREE_HANDLER = 2
_OFS_PROPERTY_ID = '_dummy_property_for_ofsfolder' # Dummy
_BTREE_PROPERTY_ID = '_tree'
_HBTREE_PROPERTY_ID = '_htree'
_HANDLER_LIST = (
  (_OFS_PROPERTY_ID, lambda self, id: None, OFSFolder2),
  (_BTREE_PROPERTY_ID, BTreeFolder2Base.__init__, CMFBTreeFolder),
  (_HBTREE_PROPERTY_ID, HBTreeFolder2Base.__init__, CMFHBTreeFolder),
)
# Bad value, accidentally put everywhere long ago
_BROKEN_BTREE_HANDLER = 'CMFBTreeFolderHandler'

class Folder(OFSFolder2, CMFBTreeFolder, CMFHBTreeFolder, Base, FolderMixIn):
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
  content_type = None # content_type is a property in ERP5, but a method in CMF

  # Per default we use BTree folder
  _folder_handler = BTREE_HANDLER
  _dummy_property_for_ofsfolder = () # Just a marker property for code simplicity (*cough*)

  # Overload __init__ so that we do not take into account title
  # This is required for test_23_titleIsNotDefinedByDefault
  def __init__(self, id):
    self.id = id

  @property
  def _count(self):
    count = self.__dict__.get('_count')
    if isinstance(count, Length) and count() > FRAGMENTED_LENGTH_THRESHOLD:
      count = self._count = FragmentedLength(count)
    return count

  @_count.setter
  def _count(self, value):
    if isinstance(value, Length) and value() > FRAGMENTED_LENGTH_THRESHOLD:
      value = FragmentedLength(value)
    self.__dict__['_count'] = value
    self._p_changed = 1

  @_count.deleter
  def _count(self):
    del self.__dict__['_count']
    self._p_changed = 1

  security.declarePublic('newContent')
  def newContent(self, *args, **kw):
    """ Create a new content """
    # Create data structure if none present
    return FolderMixIn.newContent(self, *args, **kw)

  def _getFolderHandlerData(self):
    # Internal API working around bogus _folder_handler values.
    # This method is a hot-spot for all Folder accesses. DO NOT SLOW IT DOWN.
    try:
      # Fast path: folder is sane.
      return _HANDLER_LIST[self._folder_handler]
    # Note: TypeError and not IndexError, as bogus value is a string and
    # _HANDLER_LIST only accepts integers indices.
    except TypeError:
      # Slow path: handle insane folders.
      if self._folder_handler == _BROKEN_BTREE_HANDLER:
        return _HANDLER_LIST[BTREE_HANDLER]
      raise

  security.declareProtected(Permissions.AccessContentsInformation, 'isBTree')
  def isBTree(self):
    """
    Tell if we are a BTree
    """
    return self._folder_handler in (BTREE_HANDLER, _BROKEN_BTREE_HANDLER)
  
  security.declareProtected(Permissions.AccessContentsInformation, 'isHBTree')
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
    if self._migration_in_progress or self.isHBTree():
      LOG('migrateToHBTree', WARNING,
        'Folder %s already migrated'%(self.getPath(),))
      return
    # lock folder migration
    self._migration_in_progress = True

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
    for attr in "_tree", "_mt_index", "_migration_in_progress":
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
    return self._getFolderHandlerData()[2]._initBTrees(self)

  def hashId(self, id):
    """Return a hash of id
    """
    return self._getFolderHandlerData()[2].hashId(self, id)

  def _populateFromFolder(self, source):
    """Fill this folder with the contents of another folder.
    """
    property_id, init, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      init(self, self.id)
    return folder._populateFromFolder(self, source)

  def manage_fixCount(self):
    """Calls self._fixCount() and reports the result as text.
    """
    return self._getFolderHandlerData()[2].manage_fixCount(self)

  def _fixCount(self):
    return self._getFolderHandlerData()[2]._fixCount(self)

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
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return 1
    return folder.manage_cleanup(self)

  def _cleanup(self):
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return 1
    return folder._cleanup(self)

  def _getOb(self, id, *args, **kw):
    """
    Return the named object from the folder.
    """
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      if args:
        return args[0]
      elif 'default' in kw:
        return kw['default']
      else:
        raise KeyError(id)
    return folder._getOb(self, id, *args, **kw)

  def _setOb(self, id, object):
    """Store the named object in the folder.
    """
    property_id, init, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      init(self, self.id)
    return folder._setOb(self, id, object)

  def _delOb(self, id):
    """Remove the named object from the folder.
    """
    return self._getFolderHandlerData()[2]._delOb(self, id)

  def getBatchObjectListing(self, REQUEST=None):
    """Return a structure for a page template to show the list of objects.
    """
    return self._getFolderHandlerData()[2].getBatchObjectListing(self, REQUEST)

  def manage_object_workspace(self, ids=(), REQUEST=None):
    '''Redirects to the workspace of the first object in
    the list.'''
    return self._getFolderHandlerData()[2].manage_object_workspace(self, ids, REQUEST)

  def manage_main(self, *args, **kw):
    ''' List content.'''
    return self._getFolderHandlerData()[2].manage_main.__of__(self)(self, *args, **kw)

  def tpValues(self):
    """Ensures the items don't show up in the left pane.
    """
    return self._getFolderHandlerData()[2].tpValues(self)

  def objectCount(self):
    """Returns the number of items in the folder."""
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return 0
    return folder.objectCount(self)

  def has_key(self, id):
    """Indicates whether the folder has an item by ID.
    """
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return False
    return folder.has_key(self, id)

  def getTreeIdList(self, htree=None):
    """ recursively build a list of btree ids
    """
    return self._getFolderHandlerData()[2].getTreeIdList(self, htree)

  def objectIds(self, spec=None, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return []
      assert spec is None
      if kw.has_key("base_id"):
        return CMFHBTreeFolder.objectIds(self, base_id=kw["base_id"])
      return CMFHBTreeFolder.objectIds(self)
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return []
    return folder.objectIds(self, spec)

  def objectItems(self, spec=None, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      if  self._htree is None:
        return []
      assert spec is None
      if kw.has_key("base_id"):
        return CMFHBTreeFolder.objectItems(self, base_id=kw["base_id"])
      return CMFHBTreeFolder.objectItems(self)
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return []
    return folder.objectItems(self, spec)

  def objectIds_d(self, t=None):
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return {}
    return folder.objectIds_d(self, t)

  def _checkId(self, id, allow_dup=0):
    return self._getFolderHandlerData()[2]._checkId(self, id, allow_dup)

  def _setObject(self, *args, **kw):
    property_id, init, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      init(self, self.id)
    return folder._setObject(self, *args, **kw)

  def get(self, id, default=None):
    """
    Return the named object from the folder.
    """
    return self._getFolderHandlerData()[2].get(self, id, default)

  def generateId(self, prefix='item', suffix='', rand_ceiling=999999999):
    """Returns an ID not used yet by this folder.

    The ID is unlikely to collide with other threads and clients.
    The IDs are sequential to optimize access to objects
    that are likely to have some relation.
    """
    return self._getFolderHandlerData()[2].generateId(self, prefix, suffix, rand_ceiling)

  def __getattr__(self, name):
    # Subobject ids are forbidden to start with an underscore.
    # This saves time by not even attempting traversal when not needed,
    # for example when AccessControl.users.BasicUser._check_context checks
    # whether given object is a bound function.
    if name.startswith('_'):
      raise AttributeError(name)
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      raise AttributeError(name)
    return folder.__getattr__(self, name)

  def __len__(self):
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return 0
    return folder.__len__(self)

  def keys(self, *args, **kw):
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return []
    return folder.keys(self, *args, **kw)

  def values(self, *args, **kw):
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return []
    return folder.values(self, *args, **kw)

  def items(self, *args, **kw):
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return []
    return folder.items(self, *args, **kw)

  def iteritems(self, *args, **kw):
    if self._folder_handler == HBTREE_HANDLER:
      result = CMFHBTreeFolder._htree_iteritems(self, *args, **kw)
    elif self.isBTree():
      if self._tree is None:
        return ()
      result = self._tree.iteritems(*args, **kw)
    else:
      raise NotImplementedError
    return NullIter(((x, y.__of__(self)) for x, y in result))

  def hasObject(self, id):
    property_id, _, folder = self._getFolderHandlerData()
    if getattr(self, property_id) is None:
      return False
    return folder.hasObject(self, id)

  # Work around for the performance regression introduced in Zope 2.12.23.
  # Otherwise, we use superclass' __contains__ implementation, which uses
  # objectIds, which is inefficient in HBTreeFolder2 to lookup a single key.
  __contains__ = hasObject

  # Override Zope default by folder id generation
  def _get_id(self, id):
    if self._getOb(id, None) is None :
      return id
    return self.generateNewId()

  # Implementation
  hasContent = hasObject

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
  security.declarePublic('reindexObject')
  reindexObject = Base.reindexObject

  security.declareProtected(Permissions.ModifyPortalContent,
                            'reindexObjectSecurity')
  def reindexObjectSecurity(self, *args, **kw):
    """
        Reindex security-related indexes on the object
    """
    # In ERP5, simply reindex all objects, recursively by default.
    self._getTypeBasedMethod(
      'reindexObjectSecurity',
      'recursiveReindexObject',
    )(*args, **kw)

  security.declarePublic('recursiveReindexObject')
  def recursiveReindexObject(self, activate_kw=None, **kw):
    if self.isAncestryIndexable():
      kw, activate_kw = self._getReindexAndActivateParameterDict(
        kw,
        activate_kw,
      )
      activate_kw['group_method_cost'] = 0.01
      self._recurseCallMethod(
        'immediateReindexObject',
        method_kw=kw,
        activate_kw=activate_kw,
        get_activate_kw_method_id='_updateActivateKwWithSerialisationTag',
        max_depth=None,
        skip_method_id='_isDocumentNonIndexable',
      )

  def _isDocumentNonIndexable(self, document):
    return (
      getattr(aq_base(document), 'isAncestryIndexable', None) is None or
      not document.isAncestryIndexable()
    )

  def _updateActivateKwWithSerialisationTag(self, document, activate_kw):
    activate_kw['serialization_tag'] = document.getRootDocumentPath()
    return activate_kw

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getIndexableChildValueList' )
  def getIndexableChildValueList(self):
    """
      Get indexable childen recursively.
    """
    value_list = []
    if self.isAncestryIndexable():
      value_list.append(self)
      if self.isSubtreeIndexable():
        for c in self.objectValues():
          if getattr(aq_base(c), 'getIndexableChildValueList', None) is not None:
            value_list.extend(c.getIndexableChildValueList())
    return value_list

  def _reindexOnCreation(self, **reindex_kw):
    """
    Immediately and recursively reindex self, a document which was created
    (bound to its parent) within current transaction.

    Here, immediate recursion is expected to be fine as document tree just
    created: assume we can iterate over what was just created without causing
    memory exhaustion.
    """
    self.immediateReindexObject(**reindex_kw)
    dummy = lambda **kw: None
    for document in self.objectValues():
      getattr(document, '_reindexOnCreation', dummy)(**reindex_kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'moveObject')
  def moveObject(self, idxs=None):
      """
          Reindex the object in the portal catalog.
          If idxs is present, only those indexes are reindexed.
          The metadata is always updated.

          Also update the modification date of the object,
          unless specific indexes were requested.

          Passes is_object_moved to catalog to force
          reindexing without creating new uid
      """
      if idxs is None: idxs = []
      if idxs == []:
          # Update the modification date.
          if getattr(aq_base(self), 'notifyModified', _marker) is not _marker:
              self.notifyModified()
      catalog = getattr(self.getPortalObject(), 'portal_catalog', None)
      if catalog is not None:
          catalog.moveObject(self, idxs=idxs)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'recursiveMoveObject' )
  def recursiveMoveObject(self):
    """
      Called when the base of a hierarchy is renamed
    """
    # Reindex self
    if self.isAncestryIndexable():
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
        error_list += [ConsistencyMessage(
          self, self.getRelativeUrl(), 'BTree Inconsistency (fixed)')]
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
  getObjectIds = objectIds

  # Overloading
  security.declareProtected( Permissions.AccessContentsInformation,
                             'objectValues' )
  def objectValues(self, spec=None, meta_type=None, portal_type=None,
                   sort_on=None, sort_order=None, checked_permission=None,
                   **kw):
    # Returns list of objects contained in this folder.
    #  (no docstring to prevent publishing)
    if meta_type is not None:
      spec = meta_type
    if self._folder_handler == HBTREE_HANDLER:
      if self._htree is None:
        return []
      assert spec is None
      if 'base_id' in kw:
        object_list = CMFHBTreeFolder.objectValues(self, base_id=kw['base_id'])
      else:
        object_list = CMFHBTreeFolder.objectValues(self)
    elif self.isBTree():
      if self._tree is None:
        return []
      object_list = CMFBTreeFolder.objectValues(self, spec=spec)
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
    if self._objects:
      self._objects = tuple(i for i in self._objects if i['id'] != id)
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

# See comment in Products.CMFActivity.ActivityTool about the import of BaseTool.
from Products.CMFActivity.ActivityTool import getCurrentNode

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

# Some of Folder base inherits indirectly from a different CopyContainer which
# lacks our customisations.
# Resolve all inheritence conflicts between CopyContainer (which Folder
# inherits from via Base) and those bases in favour of the property
# from Base (so it may override CopyContainer).
for CopyContainer_property_id in CopyContainer.__dict__:
  if CopyContainer_property_id.startswith('__') or CopyContainer_property_id in Folder.__dict__:
    continue
  try:
    Base_property = getattr(Base, CopyContainer_property_id)
  except AttributeError:
    continue
  if isinstance(Base_property, ClassSecurityInfo):
    continue
  setattr(Folder, CopyContainer_property_id, Base_property)
