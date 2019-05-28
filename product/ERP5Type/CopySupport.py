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

from functools import partial
from OFS import Moniker
from zExceptions import BadRequest
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permission import Permission
from OFS.ObjectManager import ObjectManager
from OFS.CopySupport import CopyContainer as OriginalCopyContainer
from OFS.CopySupport import CopyError
from OFS.CopySupport import eNotSupported, eNoItemsSpecified, eNoData
from OFS.CopySupport import eNotFound, eInvalid
from OFS.CopySupport import _cb_encode, _cb_decode, cookie_path
from OFS.CopySupport import sanity_check
from Products.ERP5Type import Permissions
from Acquisition import aq_base, aq_inner, aq_parent
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Globals import PersistentMapping, MessageDialog
from Products.ERP5Type.ImmediateReindexContextManager import ImmediateReindexContextManager
from Products.ERP5Type.Utils import get_request
from Products.ERP5Type.Message import translateString
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.CatalogTool import CatalogTool as CMFCoreCatalogTool
from Products.CMFActivity.Errors import ActivityPendingError

from cgi import escape
import sys

_marker = object()

from zLOG import LOG

class CopyContainer:
  """This class redefines the copy/paste methods  which are required in ERP5 in
  relation with the ZSQLCatalog and CMFCategory. Class using class should also
  inherit from ERP5Type.Base

    It is used as a mix-in to patch the default Zope behaviour

    It should be moved to the ZSQL Catalog sooner or later

    PLAIN UGGLY CODE: it should also be cleaned up in a way that reuses
    better the existing classes rather than copy/pasting the code
  """

  # Declarative security
  security = ClassSecurityInfo()

  # Copy / Paste support
  security.declareProtected( Permissions.AccessContentsInformation, 'manage_copyObjects' )
  def manage_copyObjects(self, ids=None, uids=None, REQUEST=None, RESPONSE=None):
      """
        Put a reference to the objects named in ids in the clip board
      """
      #LOG("Manage Copy",0, "ids:%s uids:%s" % (str(ids), str(uids)))
      if ids is not None:
        # Use default methode
        return OriginalCopyContainer.manage_copyObjects(self, ids, REQUEST,
            RESPONSE)
      if uids is None and REQUEST is not None:
          return eNoItemsSpecified
      elif uids is None:
          raise ValueError, 'uids must be specified'

      if isinstance(uids, (str, int)):
          ids=[uids]
      oblist=[]
      for uid in uids:
          ob=self.getPortalObject().portal_catalog.getObject(uid)
          if not ob.cb_isCopyable():
              raise CopyError, eNotSupported % uid
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

  def _updateInternalRelatedContent(self, object, path_item_list, new_id):
      """
       Search for categories starting with path_item_list in object and its
       subobjects, and replace the last item of path_item_list by new_id
       in matching category path.

       object
         Object to recursively check in.
       path_item_list
         Path to search for.
         Should correspond to path_item_list when the function is initially
         called - but remains identical among all recursion levels under the
         same call.
       new_id
         Id replacing the last item in path_item_list.

       Example :
        previous category value : 'a/b/c/d/e'
        path_item_list : ['a', 'b', 'c']
        new_id : 'z'
        final category value    : 'a/b/z/d/e'
      """
      for subobject in object.objectValues():
          self._updateInternalRelatedContent(object=subobject,
                                             path_item_list=path_item_list,
                                             new_id=new_id)
      changed = False
      category_list = object.getCategoryList()
      path_len = len(path_item_list)
      for position in xrange(len(category_list)):
          # only need to compare the first path_len components after the portal
          category_name = category_list[position].split('/', path_len+1)
          if category_name[1:path_len + 1] == path_item_list:
              category_name[path_len] = new_id
              category_list[position] = '/'.join(category_name)
              changed = True
      if changed:
          object.setCategoryList(category_list)

  def _recursiveSetActivityAfterTag(self, obj, activate_kw=None):
      """
      Make sure to set an after tag on each object
      so that it is possible to unindex before doing
      indexing, this prevent uid changes
      """
      uid = getattr(aq_base(obj), 'uid', None)
      if uid is not None:
        if activate_kw is None:
          activate_kw = obj.getDefaultActivateParameterDict()
        try:
          activate_kw["after_tag"] = str(uid)
        except TypeError:
          activate_kw = {"after_tag":str(uid),}
        obj.setDefaultActivateParameterDict(activate_kw)
      for sub_obj in obj.objectValues():
        self._recursiveSetActivityAfterTag(sub_obj, activate_kw)

  security.declareProtected( Permissions.ModifyPortalContent, 'manage_renameObject' )
  def manage_renameObject(self, id=None, new_id=None, REQUEST=None):
      """manage renaming an object while keeping coherency for contained
      and linked to objects inside the renamed object

      """
      ob = self._getOb(id)
      # Make sure there is no activities pending on that object
      try:
        portal_activities = self.getPortalObject().portal_activities
      except AttributeError:
        pass # There is no activity tool
      else:
        if portal_activities.countMessage(path=ob.getPath())>0:
          raise ActivityPendingError, 'Sorry, pending activities prevent ' \
                         +  'changing id at this current stage'

      # Search for categories that have to be updated in sub objects.
      self._recursiveSetActivityAfterTag(ob)
      self._updateInternalRelatedContent(object=ob,
                                         path_item_list=ob.getRelativeUrl().split("/"),
                                         new_id=new_id)
      #ob._v_is_renamed = 1
      # Rename the object
      return OriginalCopyContainer.manage_renameObject(self, id=id, new_id=new_id, REQUEST=REQUEST)

  security.declareProtected( Permissions.DeletePortalContent, 'manage_cutObjects' )
  def manage_cutObjects(self, ids=None, uids=None, REQUEST=None, RESPONSE=None):
      """ manage cutting objects, ie objects will be copied ans deleted

      """
      #LOG("Manage Copy",0, "ids:%s uids:%s" % (str(ids), str(uids)))
      if ids is not None:
        # Use default methode
        return OriginalCopyContainer.manage_cutObjects(self, ids, REQUEST)
      if uids is None and REQUEST is not None:
          return eNoItemsSpecified
      elif uids is None:
          raise ValueError, 'uids must be specified'

      if isinstance(uids, (str, int)):
          ids=[uids]
      oblist=[]
      for uid in uids:
          ob=self.getPortalObject().portal_catalog.getObject(uid)
          if not ob.cb_isMoveable():
              raise CopyError, eNotSupported % id
          m=Moniker.Moniker(ob)
          oblist.append(m.dump())
      cp=(1, oblist) # 0->1 This is the difference with manage_copyObject
      cp=_cb_encode(cp)
      if REQUEST is not None:
          resp=REQUEST['RESPONSE']
          resp.setCookie('__cp', cp, path='%s' % cookie_path(REQUEST))
          REQUEST['__cp'] = cp
          return self.manage_main(self, REQUEST)
      return cp


  security.declareProtected( Permissions.DeletePortalContent, 'manage_delObjects' )
  def manage_delObjects(self, ids=None, uids=None, REQUEST=None):
      """Delete a subordinate object

      The objects specified in 'ids' get deleted.
      """
      if ids:
        # Use default method
        return ObjectManager.manage_delObjects(self, ids, REQUEST)
      if not uids:
          return MessageDialog(title='No items specified',
                 message='No items were specified!',
                 action ='./manage_main',)
      while uids:
          uid = uids.pop()
          ob=self.getPortalObject().portal_catalog.getObject(uid)
          container = ob.aq_inner.aq_parent
          id = ob.id
          v=container._getOb(id, self)
          if v is self:
              raise BadRequest('%s does not exist' % id)
          container._delObject(id)
      if REQUEST is not None:
              return self.manage_main(self, REQUEST, update_menu=1)

  # Copy and paste support
  security.declarePrivate('manage_afterClone')
  def manage_afterClone(self, item):
    """
        Add self to the workflow.
        (Called when the object is cloned.)
    """
    #LOG("After Clone ",0, "id:%s containes:%s" % (str(item.id), str(container.id)))
    # Change uid attribute so that Catalog thinks object was not yet catalogued
    self_base = aq_base(self)
    #LOG("After Clone ",0, "self:%s item:%s" % (repr(self), repr(item)))
    #LOG("After Clone ",0, "self:%s item:%s" % (repr(self), repr(self.getPortalObject().objectIds())))
    portal = self.getPortalObject()
    self_base.uid = portal.portal_catalog.newUid()

    # Give the Owner local role to the current user, zope only does this if no
    # local role has been defined on the object, which breaks ERP5Security
    if getattr(self_base, '__ac_local_roles__', None) is not None:
      user=getSecurityManager().getUser()
      if user is not None:
        userid=user.getId()
        if userid is not None:
          #remove previous owners
          local_role_dict = self.__ac_local_roles__
          removable_role_key_list = []
          for key, value in local_role_dict.items():
            if 'Owner' in value:
              value.remove('Owner')
            if len(value) == 0:
              removable_role_key_list.append(key)
          # there is no need to keep emptied keys after cloning, it makes
          # unstable local roles -- if object is cloned it can be different when
          # after being just added
          for key in removable_role_key_list:
            local_role_dict.pop(key)
          #add new owner
          l=local_role_dict.setdefault(userid, [])
          l.append('Owner')

    # Clear the workflow history
    # XXX This need to be tested again
    if getattr(self_base, 'workflow_history', _marker) is not _marker:
      self_base.workflow_history = PersistentMapping()

    # Pass - need to find a way to pass calls...
    self.notifyWorkflowCreated()

    # Add info about copy to edit workflow
    REQUEST = get_request()
    pw = portal.portal_workflow
    if 'edit_workflow' in pw.getChainFor(self)\
        and (REQUEST is None or
            not REQUEST.get('is_business_template_installation', 0)):
      if REQUEST is not None and REQUEST.get('__cp', None):
        copied_item_list = _cb_decode(REQUEST['__cp'])[1]
        # Guess source item
        for c_item in copied_item_list:
          if c_item[-1] in item.getId():
            source_item = '/'.join(c_item)
            break
        else:
          source_item = '/'.join(copied_item_list[0])
        try:
          pw.doActionFor(self, 'edit_action', wf_id='edit_workflow',
              comment=translateString('Object copied from ${source_item}',
                            mapping=(dict(source_item=source_item))))
        except WorkflowException:
          pass
      else:
        try:
          pw.doActionFor(self, 'edit_action', wf_id='edit_workflow',
              comment=translateString('Object copied as ${item_id}',
                            mapping=(dict(item_id=item.getId()))))
        except WorkflowException:
          pass

    self.__recurse('manage_afterClone', item)

    # Call a type based method to reset so properties if necessary
    script = self._getTypeBasedMethod('afterClone')
    if callable(script):
      script()


  security.declarePrivate('manage_afterAdd')
  def manage_afterAdd(self, item, container):
      """
          Add self to the catalog.
          (Called when the object is created or moved.)
      """
      if aq_base(container) is not aq_base(self):
          #LOG("After Add ",0, "id:%s containes:%s" % (str(item.id), str(container.id)))
          if getattr(self, 'isIndexable', 0):
            self.reindexObject()
          if getattr(self, 'isIndexable', 1):
            self.__recurse('manage_afterAdd', item, container)

  security.declarePrivate('manage_beforeDelete')
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
              if getattr(aq_base(ob), name, _marker) is not _marker:
                getattr(ob, name)(*args)
              if s is None: ob._p_deactivate()

  security.declareProtected(Permissions.ModifyPortalContent, 'unindexObject')
  def unindexObject(self, path=None):
      """
          Unindex the object from the portal catalog.
      """
      if self.isIndexable:
        try:
          catalog = self.getPortalObject().portal_catalog
        except AttributeError:
          pass
        else:
          # Cleanup any failed and spawned-during-current-transaction activities for this document.
          self.flushActivity(invoke=0, only_safe=True)
          uid = getattr(self,'uid',None)
          if uid is None:
            return
          # Set the path as deleted, sql wich generate no locks
          # Set also many columns in order to make sure lines
          # marked as deleted will not be selected
          catalog.beforeUnindexObject(None,path=path,uid=uid)
          # Then start activity in order to remove lines in catalog,
          # sql wich generate locks
          # - serialization_tag is used in order to prevent unindexation to
          # happen before/in parallel with reindexations of the same object.
          catalog.activate(activity='SQLQueue',
                           tag='%s' % uid,
                           group_method_id='portal_catalog/uncatalogObjectList',
                           serialization_tag=self.getRootDocumentPath()).unindexObject(uid=uid)

  def _notifyOfCopyTo(self, container, op=0):
      """Overiden to track object cut and pastes, and update related
      content accordingly.
      The op variable is 0 for a copy, 1 for a move.
      """
      if op == 1: # move
          self._v_category_url_before_move = self.getRelativeUrl()
          self._recursiveSetActivityAfterTag(self)

  def _setId(self, id):
    # Called to set the new id of a copied object.
    # XXX It is bad to use volatile attribute, because we may have naming
    # conflict later.
    # Currently, it is required to use this volatile attribute
    # when we do a copy/paste, in order to change the relation in _postCopy.
    # Such implementation is due to the limitation of CopySuport API, which prevent
    # to pass parameter to manage_afterClone.
    self._v_previous_id = self.id
    self.id=id

  def _postCopy(self, container, op=0):
    # Called after the copy is finished to accomodate special cases.
    # The op var is 0 for a copy, 1 for a move.
    if op == 1:
      # In our case, we want to notify the category system that our path
      # changed, so that it updates related objects.
      old_url = getattr(self, '_v_category_url_before_move', None)
      if old_url is not None:
          self.activate(after_method_id='unindexObject').updateRelatedContent(
                                old_url,
                                self.getRelativeUrl())
    elif op == 0:
      # Paste a object.
      # Update related subcontent
      previous_path = self.getRelativeUrl().split('/')
      previous_path[-1] = self._v_previous_id

      self._updateInternalRelatedContent(object=self,
                                         path_item_list=previous_path,
                                         new_id=self.id)

  def _duplicate(self, cp, reindex_kw=None, immediate_reindex=False):
    _, result = self.__duplicate(
      cp,
      duplicate=True,
      is_indexable=None,
      reindex_kw=reindex_kw,
      immediate_reindex=immediate_reindex,
    )
    return result

  def __duplicate(self, cp, duplicate, is_indexable, reindex_kw, immediate_reindex):
    try:
      cp = _cb_decode(cp)
    except:
      raise CopyError(eInvalid)
    oblist = []
    op = cp[0]
    app = self.getPhysicalRoot()
    for mdata in cp[1]:
      m = Moniker.loadMoniker(mdata)
      try:
        ob = m.bind(app)
      except:
        raise CopyError(eNotFound)
      self._verifyObjectPaste(ob, validate_src=op + 1)
      oblist.append(ob)
    result = []
    def doMove(self, ob):
      aq_parent(aq_inner(ob))._delObject(ob.getId())
      return aq_base(ob)
    is_doable_id, notify_error, do_sanity_check, do, set_owner, is_clone = (
      ( # 0: Copy
        'cb_isCopyable',
        'Copy Error',
        lambda self, ob: True,
        lambda self, ob: ob._getCopy(self),
        1, # Take ownership.
        True,
      ),
      ( # 1: Move
        'cb_isMoveable',
        'Move Error',
        sanity_check,
        doMove,
        0, # Retain original ownership.
        False,
      ),
    )[op]
    for ob in oblist:
      if not getattr(ob, is_doable_id)():
        raise CopyError(eNotSupported % escape(ob.getId()))
      try:
        ob._notifyOfCopyTo(self, op=op)
      except:
        raise CopyError(MessageDialog(
          title=notify_error,
          message=sys.exc_info()[1],
          action='manage_main',
        ))
      if not do_sanity_check(self, ob):
        raise CopyError('This object cannot be pasted into itself')
      if not set_owner:
        # try to make ownership explicit so that it gets carried
        # along to the new location if needed.
        ob.manage_changeOwnershipType(explicit=1)
      new_ob = do(self, ob)
      orig_id = ob.getId()
      new_id = self._get_id(orig_id)
      result.append({'id': orig_id, 'new_id': new_id})
      new_ob._setId(new_id)
      if reindex_kw is not None:
        new_ob.setDefaultReindexParameterDict(reindex_kw)
      if is_indexable is not None and not is_indexable:
        new_ob._setNonIndexable()
      if is_clone:
        # Clear uids before spawning indexation activities, so the activity does
        # not do an uid check (as the uid is still the old one, and a new one
        # will be allocated by _postDuplicate, which must run after object gets
        # a parent).
        # Note: do not use __recurse as it only iterates over immediate content,
        # and then stop instead of calling itself into them. It relies on called
        # methods to call it back, and we do not want that for _setUid .
        todo_list = [new_ob]
        while todo_list:
          document = todo_list.pop()
          todo_list.extend(document.objectValues())
          todo_list.extend(document.opaqueValues())
          document._setUid(None)
      self._setObject(new_id, new_ob, set_owner=set_owner)
      new_ob = self._getOb(new_id)
      new_ob._postCopy(self, op=op)
      if is_clone:
        if duplicate:
          new_ob._postDuplicate()
        else:
          new_ob.manage_afterClone(new_ob)
        new_ob.wl_clearLocks()
      if not set_owner:
        # try to make ownership implicit if possible
        new_ob.manage_changeOwnershipType(explicit=0)
      method = new_ob.immediateReindexObject
      if reindex_kw is not None:
        method = partial(method, **reindex_kw)
      if isinstance(immediate_reindex, ImmediateReindexContextManager):
        immediate_reindex.append(method)
      elif immediate_reindex:
        # Immediately reindexing document that we just pasted is safe, as no
        # other transaction can by definition see it, so there cannot be a race
        # condition leading to stale catalog content.
        method()
    return op, result

  def _postDuplicate(self):
    self_base = aq_base(self)
    portal = self.getPortalObject()
    self_base.uid = portal.portal_catalog.newUid()

    # Give the Owner local role to the current user, zope only does this if no
    # local role has been defined on the object, which breaks ERP5Security
    if getattr(self_base, '__ac_local_roles__', None) is not None:
      user = getSecurityManager().getUser()
      if user is not None:
        userid = user.getId()
        if userid is not None:
          #remove previous owners
          dict = self.__ac_local_roles__
          for key, value in dict.items():
            if 'Owner' in value:
              value.remove('Owner')
          #add new owner
          l = dict.setdefault(userid, [])
          l.append('Owner')
    self.__recurse('_postDuplicate')

  def _setNonIndexable(self):
    self.isIndexable = ConstantGetter('isIndexable', value=False)

  def manage_pasteObjects(self, cb_copy_data=None, is_indexable=None, reindex_kw=None, immediate_reindex=False, REQUEST=None):
    """Paste previously copied objects into the current object.

    If calling manage_pasteObjects from python code, pass the result of a
    previous call to manage_cutObjects or manage_copyObjects as the first
    argument.

    If is_indexable is False, we will avoid indexing the pasted objects and
    subobjects

    immediate_reindex (bool)
      Immediately (=during current transaction) reindex created document, so
      it is possible to find it in catalog before transaction ends.
      Note: this does not apply to subobjects which may be created during
      pasting. Only the topmost object will be immediately reindexed. Any
      subobject will be reindexed later, using activities.

      If a ImmediateReindexContextManager instance is given, a context (in
      python sense) must have been entered with it, and indexation will
      occur when that context is exited, allowing further changes before
      first indexation (ex: workflow state change, property change).
    """
    cp = None
    if cb_copy_data is not None:
      cp = cb_copy_data
    elif REQUEST is not None and REQUEST.has_key('__cp'):
      cp = REQUEST['__cp']
    if cp is None:
      raise CopyError(eNoData)
    op, result = self.__duplicate(
      cp,
      duplicate=False,
      is_indexable=is_indexable,
      reindex_kw=reindex_kw,
      immediate_reindex=immediate_reindex,
    )
    if REQUEST is None:
      return result
    if op == 0:
      cb_dataValid = 1
    else:
      cb_dataValid = 0
      REQUEST['RESPONSE'].setCookie('__cp', 'deleted', path='%s' % cookie_path(REQUEST), expires='Wed, 31-Dec-97 23:59:59 GMT')
      REQUEST['__cp'] = None
    return self.manage_main(self, REQUEST, update_menu=1, cb_dataValid=cb_dataValid)
#### Helper methods

def tryMethodCallWithTemporaryPermission(context, permission, method,
    method_argv, method_kw, exception):
  # we want to catch the explicit security check done in manage_renameObject
  # and bypass it. for this, we temporarily give the Copy or Move right to the
  # user. We assume that if the user has enough rights to pass the
  # "declareProtected" check around "setId", he should be really able to
  # rename the object.
  try:
    return method(*method_argv, **method_kw)
  except exception:
    user = getSecurityManager().getUser()
    user_role_list = user.getRolesInContext(context)
    if len(user_role_list) > 0:
      perm_list = context.ac_inherited_permissions()
      for p in perm_list:
        if p[0] == permission:
          name, value = p[:2]
          break
      else:
        name, value = (permission, ())
      p = Permission(name,value,context)
      old_role_list = p.getRoles(default=[])
      p.setRoles(user_role_list)
      result = method(*method_argv, **method_kw)
      p.setRoles(old_role_list)
      return result
