##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#               2006 Nexedi
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Utils import deprecated
from Products.ERP5Type import Permissions


class ActionProviderBase(object):
  """
  Provide Translation Tabs and management methods for PropertyTranslationDomain
  """
  security = ClassSecurityInfo()

  security.declarePrivate('getCacheableActionList')
  def getCacheableActionList(self):
    """Return a cacheable list of enabled actions"""
    return [action.getCacheableAction()
            for action in self.getActionInformationList()
            if action.isVisible()]

  def _getActionList(self):
    action_list = self.getCacheableActionList()
    # This sort is a duplicate of calculation with what is done
    # on portal_actions.listFilteredActionsFor . But getDefaultViewFor
    # needs the sort here. This needs to be reviewed, because it is possible
    # to define in portal_actions some actions that will have higher
    # priorities than actions defined on portal types
    action_list.sort(key=lambda x:x['priority'])
    return action_list
  _getActionList = CachingMethod(_getActionList,
    id='getActionList',
    cache_factory='erp5_content_long',
    cache_id_generator=lambda method_id, *args: method_id)

  security.declarePrivate('getActionList')
  def getActionList(self):
    """Return the list of enabled actions from cache, sorted by priority"""
    return self._getActionList(self, scope=self.id)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'clearGetActionListCache')
  def clearGetActionListCache(self):
    """Clear a cache of _getRawActionInformationList."""
    self._getActionList.delete(scope=self.id)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getActionInformationList')
  def getActionInformationList(self):
    """Return all Action Information objects stored on this portal type"""
    return self.objectValues(meta_type='ERP5 Action Information')

  #
  # XXX CMF compatibility
  #

  def _importOldAction(self, old_action):
    """Convert a CMF action to an ERP5 action

    This is used to update an existing site or to import a BT.
    """
    import erp5.portal_type
    ActionInformation = getattr(erp5.portal_type, 'Action Information')
    old_action = old_action.__getstate__()
    action_type = old_action.pop('category', None)
    action_id = "action_%s" % old_action['id']
    action = ActionInformation(action_id)
    for k, v in old_action.iteritems():
      if k in ('action', 'condition', 'icon'):
        if not v:
          continue
        v = v.__class__(v.text)
      setattr(action, {'id': 'reference',
                       'priority': 'float_index',
                       'permissions': 'action_permission',
                       }.get(k, k), v)
    action.uid = None
    action = self[self._setObject(action.id, action, set_owner=0)]
    #action = self[_eventLessSetObject(self)(action.id, action, set_owner=0)]
    if action_type:
      action._setCategoryMembership('action_type', action_type)
    return action

  def _exportOldAction(self, action):
    """Convert an ERP5 action to a CMF action

    This is used to export a BT.
    """
    from Products.CMFCore.ActionInformation import ActionInformation
    old_action = ActionInformation(action.reference,
      category=action.getActionType(),
      priority=action.getFloatIndex(),
      permissions=tuple(action.getActionPermissionList()))
    for k, v in action.__dict__.iteritems():
      if k in ('action', 'condition', 'icon'):
        if not v:
          continue
        v = v.__class__(v.text)
      elif k in ('id', 'float_index', 'action_permission', 'reference'):
        continue
      setattr(old_action, k, v)
    return old_action

  security.declareProtected(Permissions.AddPortalContent, 'addAction')
  @deprecated
  def addAction(self, id, name, action, condition, permission, category,
                icon=None, visible=1, priority=1.0, REQUEST=None,
                description=None):
    """
    Not used
    """
    if isinstance(permission, basestring):
      permission = permission,
    self.newContent("action_%s" % (id,),
                    portal_type='Action Information',
                    reference=id,
                    title=name,
                    action=action,
                    condition=condition,
                    permission_list=permission,
                    action_type=category,
                    icon=icon,
                    visible=visible,
                    float_index=priority,
                    description=description)

  security.declareProtected(Permissions.ModifyPortalContent, 'deleteActions')
  @deprecated
  def deleteActions(self, selections=(), REQUEST=None):
    action_list = self.listActions()
    self.manage_delObjects([action_list[x].id for x in selections])

  security.declarePrivate('listActions')
  @deprecated
  def listActions(self, info=None, object=None):
    """ List all the actions defined by a provider."""
    return sorted(self.getActionInformationList(),
                  key=lambda x: (x.getFloatIndex(), x.getId()))

InitializeClass(ActionProviderBase)

