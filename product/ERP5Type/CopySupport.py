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

from OFS import Moniker
from AccessControl import ClassSecurityInfo
from OFS.ObjectManager import ObjectManager
from OFS.CopySupport import CopyContainer as OriginalCopyContainer
from OFS.CopySupport import _cb_encode, _cb_decode, cookie_path, absattr
from Products.ERP5Type import Permissions as Permissions
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Globals import PersistentMapping, MessageDialog

from zLOG import LOG

class CopyContainer:
  """
    This class redefines the copy/paste methods
    which are required in ERP5 in relation with the ZSQLCatalog

    It is used as a mix-in to patch the default Zope behaviour

    It should be moved to the ZSQL Catalog sooner or later

    PLAIN UGGLY CODE: it should also be cleaned up in a way that reuses
    better the existing classes rather than copy/pasting the code
  """

  # Declarative security
  security = ClassSecurityInfo()

  # Copy / Paste support
  security.declareProtected( Permissions.ViewManagementScreens, 'manage_copyObjects' )
  def manage_copyObjects(self, ids=None, uids=None, REQUEST=None, RESPONSE=None):
      """
        Put a reference to the objects named in ids in the clip board
      """
      #LOG("Manage Copy",0, "ids:%s uids:%s" % (str(ids), str(uids)))
      if ids is not None:
        # Use default methode
        return OriginalCopyContainer.manage_copyObjects(self, ids, REQUEST, RESPONSE)
      if uids is None and REQUEST is not None:
          return eNoItemsSpecified
      elif uids is None:
          raise ValueError, 'uids must be specified'

      if type(uids) is type(''):
          ids=[uids]
      if type(uids) is type(1):
          ids=[uids]
      oblist=[]
      for uid in uids:
          ob=self.portal_catalog.getObject(uid)
          if not ob.cb_isCopyable():
              raise CopyError, eNotSupported % id
          m=Moniker.Moniker(ob)
          oblist.append(m.dump())
      cp=(0, oblist)
      cp=_cb_encode(cp)
      if REQUEST is not None:
          resp=REQUEST['RESPONSE']
          resp.setCookie('__cp', cp, path='%s' % cookie_path(REQUEST))
          REQUEST['__cp'] = cp
          return self.manage_main(self, REQUEST)
      return cp

  security.declareProtected( Permissions.DeletePortalContent, 'manage_delObjects' )
  def manage_delObjects(self, ids=[], uids=[], REQUEST=None):
      """Delete a subordinate object

      The objects specified in 'ids' get deleted.
      """
      if len(ids) > 0:
        # Use default method
        return ObjectManager.manage_delObjects(self, ids, REQUEST)
      if type(uids) is type(''): ids=[uids]
      if type(uids) is type(1): ids=[uids]
      if not uids:
          return MessageDialog(title='No items specified',
                 message='No items were specified!',
                 action ='./manage_main',)
      while uids:
          uid=uids[-1]
          ob=self.portal_catalog.getObject(uid)
          container = ob.aq_inner.aq_parent
          id = ob.id
          v=container._getOb(id, self)
          if v is self:
              raise 'BadRequest', '%s does not exist' % ids[-1]
          container._delObject(id)
          del uids[-1]
      if REQUEST is not None:
              return self.manage_main(self, REQUEST, update_menu=1)


  # Copy and paste support
  def manage_afterClone(self, item):
    """
        Add self to the workflow.
        (Called when the object is cloned.)
    """
    #LOG("After Clone ",0, "id:%s containes:%s" % (str(item.id), str(container.id)))
    # Change uid attribute so that Catalog thinks object was not yet catalogued
    self_base = aq_base(self)
    self_base.uid = None
    # Clear the workflow history
    # XXX This need to be tested again
    if hasattr(self_base, 'workflow_history'):
      self_base.workflow_history = PersistentMapping()

    # Pass - need to find a way to pass calls...
    self.notifyWorkflowCreated()
    self.__recurse('manage_afterClone', item)
    # Reindex object
    self.reindexObject()
    #self.flushActivity(invoke=1)

  def manage_afterAdd(self, item, container):
      """
          Add self to the catalog.
          (Called when the object is created or moved.)
      """
      if aq_base(container) is not aq_base(self):
          #LOG("After Add ",0, "id:%s containes:%s" % (str(item.id), str(container.id)))
          if self.isIndexable:
            self.reindexObject()
            self.__recurse('manage_afterAdd', item, container)

  def manage_beforeDelete(self, item, container):
      """
          Remove self from the catalog.
          (Called when the object is deleted or moved.)
      """
      if aq_base(container) is not aq_base(self):
          self.__recurse('manage_beforeDelete', item, container)
          if self.isIndexable:
            self.unindexObject()

  def __recurse(self, name, *args):
      """
          Recurse in both normal and opaque subobjects.
      """
      values = self.objectValues()
      opaque_values = self.opaqueValues()
      for subobjects in values, opaque_values:
          for ob in subobjects:
              s = getattr(ob, '_p_changed', 0)
              if hasattr(aq_base(ob), name):
                getattr(ob, name)(*args)
              if s is None: ob._p_deactivate()

  security.declareProtected(Permissions.ModifyPortalContent, 'unindexObject')
  def unindexObject(self, path=None):
      """
          Unindex the object from the portal catalog.
      """
      if self.isIndexable:
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is not None:
            self.flushActivity(invoke=0)
            #LOG("after flush",0, str(self.id))
            catalog.unindexObject(self, path=path)
            #LOG("unindexObject",0, str(self.id))

  security.declareProtected(Permissions.ModifyPortalContent, 'moveObject')
  def moveObject(self, idxs=[]):
      """
          Reindex the object in the portal catalog.
          If idxs is present, only those indexes are reindexed.
          The metadata is always updated.

          Also update the modification date of the object,
          unless specific indexes were requested.

          Passes is_object_moved to catalog to force
          reindexing without creating new uid
      """
      if idxs == []:
          # Update the modification date.
          if hasattr(aq_base(self), 'notifyModified'):
              self.notifyModified()
      catalog = getToolByName(self, 'portal_catalog', None)
      if catalog is not None:
          catalog.moveObject(self, idxs=idxs)


