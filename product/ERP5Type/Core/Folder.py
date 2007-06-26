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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_self
from OFS.History import Historical
import ExtensionClass

from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore import CMFCorePermissions

from Products.ERP5Type.Base import Base
from Products.ERP5Type.CopySupport import CopyContainer
from Products.ERP5Type import PropertySheet, Permissions
from Products.ERP5Type.XMLExportImport import Folder_asXML
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Utils import sortValueList

try:
  from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder
except ImportError:
  from Products.BTreeFolder2.CMFBTreeFolder import CMFBTreeFolder
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from AccessControl import getSecurityManager
from Products.ERP5Type import Permissions
from random import randint

import os

from zLOG import LOG, PROBLEM
import warnings

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

  security.declarePublic('newContent')
  def newContent(self, id=None, portal_type=None, id_group=None,
          default=None, method=None, immediate_reindex=0,
          container=None, created_by_builder=0, activate_kw=None,
          is_indexable=None, temp_object=0, **kw):
    """Creates a new content.
    This method is public, since TypeInformation.constructInstance will perform
    the security check.
    """
    pt = self._getTypesTool()
    if container is None:
      container = self
    if id is None:
      new_id = str(container.generateNewId( id_group=id_group,
                                            default=default,
                                            method=method))
    else:
      new_id = str(id)
    if portal_type is None:
      # XXX This feature is very confusing
      # And made the code more difficult to update
      portal_type = container.allowedContentTypes()[0].id

    if temp_object:
      from Products.ERP5Type import Document
      # we get an object from factory only for first temp container object
      # otherwise we get an id so we can use the classic way
      if not getattr(container, 'isTempObject', lambda: 0)():
        factory_name = 'newTemp%s' %(portal_type.replace(' ', ''))
        m = getattr(Document, factory_name)
        return m(container, new_id)

    myType = pt.getTypeInfo(container)
    if myType is not None:
      if not myType.allowType( portal_type ):
        if not 'portal_trash' in container.getPhysicalPath():
          raise ValueError('Disallowed subobject type: %s' % portal_type)

    pt.constructContent( type_name=portal_type,
                         container=container,
                         id=new_id,
                         created_by_builder=created_by_builder,
                         activate_kw=activate_kw,
                         is_indexable=is_indexable
                         ) # **kw) removed due to CMF bug
    # TODO :the **kw makes it impossible to create content not based on
    # ERP5TypeInformation, because factory method often do not support
    # keywords arguments.

    new_instance = container[new_id]
    if kw != {} : new_instance._edit(force_update=1, **kw)
    if immediate_reindex: new_instance.immediateReindexObject()
    return new_instance

  security.declareProtected(
            Permissions.DeletePortalContent, 'deleteContent')
  def deleteContent(self, id):
    """ delete items in this folder.
      `id` can be a list or a string.
    """
    if isinstance(id, str):
      self._delObject(id)
    elif isinstance(id, list) or isinstance(id, tuple):
      for my_id in id:
        self._delObject(my_id)
    else:
      raise TypeError, 'deleteContent only accepts string or list, '\
                       'not %s' % type(id)

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
      my_id = int(self.getLastId())
    except TypeError:
      my_id = 1
    while self.hasContent(str(my_id)):
      my_id = my_id + 1
    my_id = str(my_id)
    self._setLastId(my_id) # Make sure no reindexing happens
    return my_id

  # Automatic ID Generation method
  security.declareProtected(Permissions.View, 'generateNewId')
  def generateNewId(self,id_group=None,default=None,method=None):
    """
      Generate a new Id which has not been taken yet in this folder.
      Eventually increment the id number until an available id
      can be found

      Permission is view because we may want to add content to a folder
      without changing the folder content itself.
      XXX
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
          idGenerator = self._generateNextId
      else:
        idGenerator = self._generateNextId
      my_id = idGenerator()
      while self.hasContent(my_id):
        my_id = self._generateNextId()
    else:
      my_id = str(self.portal_ids.generateNewId( id_group=id_group,
                                                 default=default,
                                                 method=method ))
    return my_id

  security.declareProtected(Permissions.View, 'hasContent')
  def hasContent(self,id):
    return self.hasObject(id)

  # Get the content
  security.declareProtected(Permissions.View, 'searchFolder')
  def searchFolder(self, **kw):
    """
      Search the content of a folder by calling
      the portal_catalog.
    """
    if not kw.has_key('parent_uid'): #WHY ????
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

    kw2 = {}
    # Remove useless matter before calling the
    # catalog. In particular, consider empty
    # strings as None values
    for cname in kw.keys():
      if kw[cname] != '' and kw[cname] != None:
        kw2[cname] = kw[cname]
    # The method to call to search the folder
    # content has to be called z_search_folder
    method = self.portal_catalog.portal_catalog
    return method(**kw2)

  security.declareProtected(Permissions.View, 'countFolder')
  def countFolder(self, **kw):
    """
      Search the content of a folder by calling
      the portal_catalog.
    """
    if not kw.has_key('parent_uid'): #WHY ????
      kw['parent_uid'] = self.getUid()

    # Make sure that if we use parent base category
    # We do not have conflicting parent uid values
    delete_parent_uid = 0
    if kw.has_key('selection_domain'):
      if kw['selection_domain'].asDomainDict().has_key('parent'):
        delete_parent_uid = 1
    if kw.has_key('selection_report'):
      if kw['selection_report'].asDomainDict().has_key('parent'):
        delete_parent_uid = 1
    if delete_parent_uid:
      del kw['parent_uid']

    kw2 = {}
    # Remove useless matter before calling the
    # catalog. In particular, consider empty
    # strings as None values
    for cname in kw.keys():
      if kw[cname] != '' and kw[cname]!=None:
        kw2[cname] = kw[cname]
    # The method to call to search the folder
    # content has to be called z_search_folder
    method = self.portal_catalog.countResults
    return method(**kw2)

  # Count objects in the folder
  security.declarePrivate('_count')
  def _count(self, **kw):
    """
      Returns the number of items in the folder.
    """
    return self.countFolder(**kw)[0][0]

class Folder( CopyContainer, CMFBTreeFolder, Base, FolderMixIn):
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
  or display content. This requires a method called
  *z_search_folder* to be put inside the ZSQLCatalog object
  of the ERP5 portal.

  An ERP5 Binder document class will eventually be defined
  in order to implement a binder of documents which can itself
  be categorized.
  """

  meta_type = 'ERP5 Folder'
  portal_type = 'Folder'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

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
                    )

  # Class inheritance fixes
  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  edit = Base.edit
  security.declareProtected( Permissions.ModifyPortalContent, '_edit' )
  _edit = Base._edit
  _setPropValue = Base._setPropValue
  _propertyMap = Base._propertyMap # are there any others XXX ?
  # XXX Prevent inheritance from PortalFolderBase
  description = None


  # Overload __init__ so that we do not take into account title
  # This is required for test_23_titleIsNotDefinedByDefault
  def __init__(self, id):
    self.id = id
    BTreeFolder2Base.__init__(self, id)

  # Override Zope default by folder id generation
  def _get_id(self, id):
    if self._getOb(id, None) is None :
      return id
    return self.generateNewId()

  #security.declareProtected( Permissions.DeletePortalContent, 'manage_delObjects' )
  #manage_delObjects = CopyContainer.manage_delObjects

  # Implementation
#   security.declarePrivate('_setObject')
#   def _setObject(self, id, object, roles=None, user=None, set_owner=1):
#     """
#       This method is here in order to dynamically update old
#       folders into the new BTree folder type.
#       This method is destructive in the sens that objects
#       of the old folder will be lost during the update
#     """
#     # First make sur the folder has been initialized
#     if not hasattr(self, '_tree'):
#       CMFBTreeFolder.__init__(self, self.id)
#     if not self._tree:
#       CMFBTreeFolder.__init__(self, self.id)
#     # Then insert the object
#     CMFBTreeFolder._setObject(self, id, object, roles=roles, user=user, set_owner=set_owner)
# This method destroys the title when we create new object in empty folder

  security.declareProtected(Permissions.View, 'hasContent')
  def hasContent(self,id):
    return self.hasObject(id)

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
      get_transaction().commit()

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
      #get_transaction().commit(1)
      get_transaction().commit() # we may use commit(1) some day XXX
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
      get_transaction().commit()
      if hasattr(obase, 'updateAll'):
        update_list += o.updateAll(filter=filter, \
                              method=method, test_after=test_after,request=request,include=0,**kw)

    return update_list

  security.declareProtected( Permissions.ModifyPortalContent, 'upgradeObjectClass' )
  def upgradeObjectClass(self, test_before=None, from_class=None,\
                         to_class=None, test_after=None):
    """
    upgrade the class of all objects inside this
    particular folder
     test have to be a method with one parameter
     migrations is a dictionnary of class, { from_class : to_class }
    """
    #LOG("upradeObjectClass: folder ",0,self.id)
    test_list = []
    folder = self.getObject()
    for o in self.listFolderContents():
      # Make sure this sub object is not the same as object
      if o.getPhysicalPath() != self.getPhysicalPath():
        id = o.getId()
        obase = aq_base(o)
        # Check if the subobject have to also be upgraded
        if hasattr(obase,'upgradeObjectClass'):
          test_list += o.upgradeObjectClass(test_before=test_before, \
                          from_class=from_class, to_class=to_class,
                          test_after=test_after)
        # Test if we must apply the upgrade
        if test_before(o) is not None:
          LOG("upradeObjectClass: id ",0,id)
          klass = obase.__class__
          LOG("upradeObjectClass: klass ",0,str(klass))
          LOG("upradeObjectClass: from_class ",0,str(from_class))
          if klass == from_class:
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
            LOG("upradeObjectClass: ",0,"add new object: %s" % str(newob.id))
            get_transaction().commit() # XXX this commit should be after _setObject
            LOG("upradeObjectClass: ",0,"newob.__class__: %s" % str(newob.__class__))
            self._setObject(id, newob)
            object_to_test = self._getOb(id)
            test_list += test_after(object_to_test)

    return test_list


  # Catalog related
  security.declarePublic( 'reindexObject' )
  def reindexObject(self, *args, **kw):
    """
      Fixes the hierarchy structure (use of Base class)
      XXXXXXXXXXXXXXXXXXXXXXXX
      BUG here : when creating a new base category
    """
    return Base.reindexObject(self, *args, **kw)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'reindexObjectSecurity')
  def reindexObjectSecurity(self):
    """
        Reindex security-related indexes on the object
        (and its descendants).
    """
    # In ERP5, simply reindex all objects.
    self.recursiveReindexObject()

  security.declarePublic( 'recursiveReindexObject' )
  def recursiveReindexObject(self, activate_kw=None, **kw):
    """
      Fixes the hierarchy structure (use of Base class)
      XXXXXXXXXXXXXXXXXXXXXXXX
      BUG here : when creating a new base category
    """
    if self.isIndexable:
      if activate_kw is None:
        activate_kw = {}

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
                          spec=(), filter=None, portal_type=(), base=0 ):
    if category == 'content':
      content_list = self.searchFolder(portal_type=spec)
      return map(lambda x: x.relative_url, content_list)
    else:
      return Base.getCategoryMembershipList(self, category,
          spec=spec, filter=filter, portal_type=portal_type, base=base)

  # Alias - class inheritance resolution
  security.declareProtected( Permissions.View, 'Title' )
  Title = Base.Title

  security.declareProtected(Permissions.AccessContentsInformation,
                            'checkConsistency')
  def checkConsistency(self, fixit=0):
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
        get_transaction().commit(1)
        error_list += [(self.getRelativeUrl(), 'BTree Inconsistency',
                       199, '(fixed)')]
    # Call superclass
    error_list += Base.checkConsistency(self, fixit=fixit)
    # We must commit before listing folder contents
    # in case we erased some data
    if fixit:
      get_transaction().commit(1)
    # Then check the consistency on all sub objects
    for obj in self.contentValues():
      if fixit:
        extra_errors = obj.fixConsistency()
      else:
        extra_errors = obj.checkConsistency()
      if len(extra_errors) > 0:
        error_list += extra_errors
    # We should also return an error if any
    return error_list

  security.declareProtected( Permissions.AccessContentsInformation, 'asXML' )
  def asXML(self, ident=0):
    """
        Generate an xml text corresponding to the content of this object
    """
    return Folder_asXML(self,ident=ident)

  # Optimized Menu System
  security.declarePublic('getVisibleAllowedContentTypeList')
  def getVisibleAllowedContentTypeList(self):
    """
      List portal_types' names wich can be added in this folder / object.
      Cache results.

      This function is *much* similar to allowedContentTypes, except it does
      not returns portal types but their ids and filter out those listed as
      hidden content types. It allows to be much faster when only the type id
      is needed.
    """
    if not getSecurityManager().checkPermission(
                      Permissions.AddPortalContent, self):
      return []

    portal = self.getPortalObject()

    def _getVisibleAllowedContentTypeList():
      hidden_type_list = portal.portal_types.getTypeInfo(self)\
                                              .getHiddenContentTypeList()
      return [ ti.id for ti in CMFBTreeFolder.allowedContentTypes(self)
               if ti.id not in hidden_type_list ]

    user = str(_getAuthenticatedUser(self))
    portal_type = self.getPortalType()
    portal_path = portal.getPhysicalPath()

    _getVisibleAllowedContentTypeList = CachingMethod(
        _getVisibleAllowedContentTypeList,
        id=("_getAllowedContentTypeTitleList", user, portal_path, portal_type),
        cache_factory='erp5_content_long')
    return _getVisibleAllowedContentTypeList()

  security.declarePublic('allowedContentTypes')
  def allowedContentTypes( self ):
    """ List portal_types which can be added in this folder / object.
        Cache results.
        Only paths are cached, because we must not cache objects.
        This makes the result, even if based on cache, O(n) so it becomes quite
        costly with many allowed content types.
        Example:
         on Person (12 allowed content types): 1000 calls take 3s.
         on Person Module (1 allowed content type): 1000 calls take 0.3s.
    """
    # if we don't have add portal content permission, return directly.
    # this prevents returning cached allowed types when the user no longer have
    # the permission to any content type. (security definitions in workflows
    # usually remove some permission once an object is "Valid")
    # This also prevents filling the cache with an empty list, when the user
    # does not have the permission to add any content yet.

    # XXX this works just fine, unless some objects can be added with another
    # permission that "Add portal content". For now, this is only the case for
    # Role Definition objects, but this shows that generally speaking, this is
    # not the right approach.
    if not getSecurityManager().checkPermission(
                      Permissions.AddPortalContent, self):
      return []

    def _allowedContentTypes( portal_type=None, user=None, portal_path=None ):
      # Sort the list for convenience -yo
      # XXX This is not the best solution, because this does not take
      # account i18n into consideration.
      # XXX So sorting should be done in skins, after translation is performed.
      def compareTypes(a, b): return cmp(a.title or a.id, b.title or b.id)
      type_list = CMFBTreeFolder.allowedContentTypes(self)
      type_list.sort(compareTypes)
      return ['/'.join(x.getPhysicalPath()) for x in type_list]

    _allowedContentTypes = CachingMethod( _allowedContentTypes,
                                          id = 'allowedContentTypes',
                                          cache_factory = 'erp5_content_long')
    user = str(_getAuthenticatedUser(self))
    portal_type = self.getPortalType()
    portal = self.getPortalObject()
    portal_path = portal.getPhysicalPath()
    return [portal.restrictedTraverse(path) for path in
              _allowedContentTypes( portal_type = portal_type,
                                    user = user,
                                    portal_path = portal_path )]

  # Multiple Inheritance Priority Resolution
  _setProperty = Base._setProperty
  setProperty = Base.setProperty
  getProperty = Base.getProperty
  hasProperty = Base.hasProperty
  view = Base.view

  # Aliases
  getObjectIds = CMFBTreeFolder.objectIds

  # Overloading
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentSQLExpression' )
  def getParentSQLExpression(self, table = 'catalog', strict_membership = 0):
    """
      Builds an SQL expression to search children and subclidren
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
      object_url = object.getRelativeUrl()
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
                   sort_on=None, sort_order=None, **kw):
    """
    Returns a list containing object contained in this folder.
    """
    if meta_type is not None:
      spec = meta_type
    # when an object inherits from Folder after it was instanciated, it lacks
    # its BTreeFolder properties.
    if getattr(self, '_tree', None) is None:
      try:
        self._initBTrees()
      except AttributeError:
        from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
        BTreeFolder2Base.__init__(self, self.getId())
    object_list = CMFBTreeFolder.objectValues(self, spec=spec)
    if portal_type is not None:
      if type(portal_type) == type(''):
        portal_type = (portal_type,)
      object_list = filter(lambda x: x.getPortalType() in portal_type,
                           object_list)
    object_list = sortValueList(object_list, sort_on, sort_order, **kw)
    return object_list

  security.declareProtected( Permissions.AccessContentsInformation,
                             'contentValues' )
  def contentValues(self, spec=None, meta_type=None, portal_type=None,
                    sort_on=None, sort_order=None, **kw):
    """
    Returns a list containing object contained in this folder.
    Filter objects with appropriate permissions (as in contentValues)
    """
    if meta_type is not None:
      spec = meta_type
    if portal_type is not None:
      kw['portal_type'] = portal_type
    filter = kw.pop('filter', {}) or {}
    kw.update(filter)
    object_list = CMFBTreeFolder.contentValues(self, spec=spec, filter=kw)
    object_list = sortValueList(object_list, sort_on, sort_order, **kw)
    return object_list

  # Override security declaration of CMFCore/PortalFolder (used by CMFBTreeFolder)
  security.declareProtected(Permissions.ModifyPortalContent,'setDescription')
  security.declareProtected( Permissions.ModifyPortalContent, 'setTitle' )

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

      TODO:
         - prevent from changing templates or invoking workflows
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

  def _delObject(self, id, dp=1):
    """
      _delObject is redefined here in order to make sure
      we do not do silent except while we remove objects
      from catalog
    """
    object = self._getOb(id)
    object.manage_beforeDelete(object, self)
    self._delOb(id)

  security.declareProtected( CMFCorePermissions.ManagePortal, 'callMethodOnObjectList' )
  def callMethodOnObjectList(self, object_path_list, method_id, *args, **kw):
    """
    Very usefull if we want to activate the call of a method
    on many objects at a time. Like this we could prevent creating
    too much acitivities at a time, and we may have only the path

    """
    portal = self.getPortalObject()
    for object_path in object_path_list:
      current_object = portal.unrestrictedTraverse(object_path)
      method = getattr(current_object, method_id, None)
      if method is None:
        raise ValueError, "The method %s was not found" % method_id
      method(*args, **kw)

# Overwrite Zope setTitle()
Folder.setTitle = Base.setTitle
