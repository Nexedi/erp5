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
import ExtensionClass

from Products.CMFCore.utils import _getAuthenticatedUser

from Products.ERP5Type.Base import Base
from Products.ERP5Type.CopySupport import CopyContainer
from Products.ERP5Type import PropertySheet, Permissions
from Products.ERP5Type.XMLExportImport import Folder_asXML
from Products.ERP5Type.Cache import CachingMethod

from Products.BTreeFolder2.CMFBTreeFolder import CMFBTreeFolder

import os

from zLOG import LOG

# Dummy Functions for update / upgrade
def dummyFilter(object,REQUEST=None):
  return 1

def dummyTestAfter(object,REQUEST=None):
  return []

class FolderMixIn(ExtensionClass.Base):

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  security.declareProtected(Permissions.AddPortalContent, 'newContent')
  def newContent(self, id=None, portal_type=None, id_group=None, default=None, method=None, immediate_reindex=0, **kw):
    """
      Creates a new content
    """
    if id is None:
      new_id = str(self.generateNewId(id_group = id_group, default=default, method=method))
    else:
      new_id = str(id)
    if portal_type is None: portal_type = self.allowedContentTypes()[0].id
    self.portal_types.constructContent(type_name=portal_type,
                                       container=self,
                                       id=new_id,
                                       ) # **kw) removed due to CMF bug
    new_instance = self[new_id]
    if kw is not None: new_instance._edit(force_update=1, **kw)
    if immediate_reindex: new_instance.immediateReindexObject()
    return new_instance

  security.declareProtected(Permissions.DeletePortalContent, 'deleteContent')
  def deleteContent(self, id):
    # id is string or list
    # XXX should raise error if not
    if type(id) is type(''):
      self._delObject(id)
    elif type(id) is type([]) or type(id) is type(()):
      for my_id in id:
        self._delObject(my_id)

  # Automatic ID Generation method
  security.declareProtected(Permissions.View, 'generateNewId')
  def generateNewId(self,id_group=None,default=None,method=None):
      """
        Generate a new Id which has not been taken yet in this folder.
        Eventually increment the id number until an available id
        can be found

        Permission is view because we may want to add content to a folder
        without changing the folder content itself. XXXXXXXXXXX
        XXXXXXXXXXXX
      """
      my_id = None
      if id_group is None:
        id_group = self.getIdGroup()
        LOG('newId', 0, repr(( 'id_group was None', id_group )))
      if id_group is None or id_group=='None':
        try:
          my_id = int(self.getLastId())
          LOG('newId', 0, repr(( 'id_group is None, my_id', my_id )))
        except:
          my_id = 1
          LOG('newId', 0, repr(( 'id_group is None, my_id failed', my_id )))
        while self.hasContent(str(my_id)):
          LOG('newId', 0, repr(( 'my_id already there', my_id )))
          my_id = my_id + 1
        self._setLastId(str(my_id)) # Make sure no reindexing happens
      else:
        my_id = self.portal_ids.generateNewId(id_group=id_group,default=default,method=method)
        LOG('newId', 0, repr(( 'id_group is', id_group, my_id )))

      return str(my_id)

  security.declareProtected(Permissions.View, 'hasContent')
  def hasContent(self,id):
    return id in self.objectIds()

  # Get the content
  security.declareProtected(Permissions.View, 'searchFolder')
  def searchFolder(self, **kw):
    """
      Search the content of a folder by calling
      the portal_catalog.
    """
    if not kw.has_key('parent_uid'): #WHY ????
      kw['parent_uid'] = self.uid
    kw2 = {}
    # Remove useless matter before calling the
    # catalog. In particular, consider empty
    # strings as None values
    for cname in kw.keys():
      if kw[cname] != '' and kw[cname]!=None:
        kw2[cname] = kw[cname]
    # The method to call to search the folder
    # content has to be called z_search_folder
    method = self.portal_catalog.portal_catalog
    return method(**kw2)

  # Count objects in the folder
  security.declarePrivate('_count')
  def _count(self, **kw):
    """
      Returns the number of items in the folder.
    """
    # PERFORMANCE PROBLEM
    # This should be improved in order to use
    # SQL counting
    return len(self.searchFolder(**kw))


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

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.SimpleItem
                    , PropertySheet.Folder
                    )

  # CMF Factory Type Information
  factory_type_information = \
         { 'id'           : portal_type
         , 'meta_type'    : meta_type
         , 'description'  : """\
Folders allow to store a large number of documents (1,000,000 should not
be a problem)."""
         , 'icon'     : 'folder_icon.gif'
         , 'product'  : 'ERP5Type'
         , 'factory'  : 'addFolder'
         , 'filter_content_types' : 0
         , 'immediate_view' : 'Base_metadataView'
         , 'actions'  :
        ( { 'id'    : 'view'
          , 'name'    : 'View'
          , 'action'  : 'Folder_list'
          , 'permissions'   : (Permissions.View,)
          , 'category'  : 'object_view'
          }
        , { 'id'    : 'list'
          , 'name'    : 'List'
          , 'action'  : 'Folder_list'
          , 'permissions'   : (Permissions.View,)
          , 'category'  : 'object'
          }
        , { 'id'    : 'localroles'
          , 'name'    : 'Local Roles'
          , 'action'  : 'folder_localrole_form'
          , 'permissions'   :  (Permissions.ManageProperties,)
          , 'category'  : 'object_view'
          }
        , { 'id'    : 'syndication'
          , 'name'    : 'Syndication'
          , 'action'  : 'synPropertiesForm'
          , 'permissions'   : (Permissions.ManageProperties,)
          , 'category'  : 'object_view'
          }
        , { 'id'    : 'metadata'
          , 'name'    : 'Metadata'
          , 'action'  : 'Base_metadataView'
          , 'permissions'   : (Permissions.ManageProperties,)
          , 'category'  : 'object_view'
          }
        )
        }

  # Class inheritance fixes
  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  edit = Base.edit
  security.declareProtected( Permissions.ModifyPortalContent, '_edit' )
  _edit = Base._edit
  _setPropValue = Base._setPropValue

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

  security.declareProtected( Permissions.ModifyPortalContent, 'recursiveApply' )
  def recursiveApply(self, filter=dummyFilter, method=None, test_after=dummyTestAfter, include=1, REQUEST=None, **kw):
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
    LOG('Folder, updateAll ',0,"first one self.path: %s" % self.getPath())

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
    LOG("upradeObjectClass: folder ",0,self.id)
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
            except:
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

  security.declarePublic( 'recursiveReindexObject' )
  def recursiveReindexObject(self, *args, **kw):
    """
      Fixes the hierarchy structure (use of Base class)
      XXXXXXXXXXXXXXXXXXXXXXXX
      BUG here : when creating a new base category
    """
    self.activate().recursiveImmediateReindexObject(*args, **kw)

  security.declarePublic( 'recursiveImmediateReindexObject' )
  def recursiveImmediateReindexObject(self, *args, **kw):
      """
        Applies immediateReindexObject recursively
      """
      # Reindex self
      self.flushActivity(invoke = 0, method_id='immediateReindexObject') # This might create a recursive lock
      self.flushActivity(invoke = 0, method_id='recursiveImmediateReindexObject') # This might create a recursive lock
      if self.isIndexable:
        self.immediateReindexObject(*args, **kw)
      # Reindex contents
      for c in self.objectValues():
        if hasattr(aq_base(c), 'recursiveImmediateReindexObject'):
          c.recursiveImmediateReindexObject(*args, **kw)

  security.declarePublic( 'recursiveQueueCataloggedObject' )
  def recursiveQueueCataloggedObject(self, *args, **kw):
      """
        Apply queueCataloggedObject recursively
      """
      # Index self
      self.flushActivity(invoke = 0, method_id='queueCataloggedObject') # This might create a recursive lock
      self.flushActivity(invoke = 0, method_id='recursiveQueueCataloggedObject') # This might create a recursive lock
      if self.isIndexable:
        self.queueCataloggedObject(*args, **kw)
      # Index contents
      for c in self.objectValues():
        if hasattr(aq_base(c), 'recursiveQueueCataloggedObject'):
          c.recursiveQueueCataloggedObject(*args, **kw)

  security.declareProtected( Permissions.ModifyPortalContent, 'recursiveMoveObject' )
  def recursiveMoveObject(self):
    """
      Called when the base of a hierarchy is renamed
    """
    # Reindex self
    if self.isIndexable:
      self.moveObject()
    # Reindex contents
    for c in self.objectValues():
      if hasattr(aq_base(c), 'recursiveMoveObject'):
        c.recursiveMoveObject()

  # Special Relation keyword : 'content' and 'container'
  security.declareProtected( Permissions.AccessContentsInformation, '_getCategoryMembershipList' )
  def _getCategoryMembershipList(self, category,
                          spec=(), filter=None, portal_type=(), base=0 ):
    if category == 'content':
      content_list = self.searchFolder(portal_type=spec)
      return map(lambda x: x.relative_url, content_list)
    else:
      return Base.getCategoryMembershipList(self, category,
          spec=spec, filter=filter, portal_type=portal_type,  base=base)

  # Alias - class inheritance resolutino
  security.declareProtected( Permissions.View, 'Title' )
  Title = Base.Title

  security.declareProtected(Permissions.AccessContentsInformation, 'checkConsistency')
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
        get_transaction().commit() # We must commit if we want to keep on recursing
        error_list += [(self.getRelativeUrl(), 'BTree Inconsistency', 199, '(fixed)')]
    # Call superclass
    error_list += Base.checkConsistency(self, fixit=fixit)
    if fixit: get_transaction().commit() # We must commit before listing folder contents
                                         # in case we erased some data
    # Then check the consistency on all sub objects
    for object in self.contentValues():
      if fixit:
        extra_errors = object.fixConsistency()
      else:
        extra_errors = object.checkConsistency()
      if len(extra_errors) > 0:
        error_list += extra_errors
        # Commit after each subobject
        #if fixit:
        try:
          get_transaction().commit()
        except:
          LOG("Folder WARNING",0,
            "Could not commit checkConsistency transaction for object %s" % object.getRelativeUrl())



    # We should also return an error if any
    return error_list

  security.declareProtected( Permissions.AccessContentsInformation, 'asXML' )
  def asXML(self, ident=0):
    """
        Generate an xml text corresponding to the content of this object
    """
    return Folder_asXML(self,ident=ident)

  # Optimized Menu System
  security.declarePublic('allowedContentTypes')
  def allowedContentTypes( self ):
    """
      List portal_types which can be added in this folder / object.
      Cache results. This requires restarting Zope to update values.
    """
    def _allowedContentTypes(portal_type=None, user=None):
      # Sort the list for convenience -yo
      # XXX This is not the best solution, because this does not take account i18n into consideration.
      # XXX So sorting should be done in skins, after translation is performed.
      def compareTypes(a, b): return cmp(a.title or a.id, b.title or b.id)
      type_list = CMFBTreeFolder.allowedContentTypes(self)
      type_list.sort(compareTypes)
      return type_list

    _allowedContentTypes = CachingMethod(_allowedContentTypes, id='allowedContentTypes', cache_duration = 300)
    user = str(_getAuthenticatedUser(self))
    portal_type = self.getPortalType()
    return _allowedContentTypes(portal_type=portal_type, user=user)


  # Multiple Inheritance Priority Resolution
  _setProperty = Base._setProperty
  setProperty = Base.setProperty
  getProperty = Base.getProperty
  hasProperty = Base.hasProperty
  view = Base.view

  # Aliases
  getObjectIds = CMFBTreeFolder.objectIds


