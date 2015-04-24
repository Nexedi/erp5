##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Julien Muchembled <jm@nexedi.com>
#                    Boris Kocherov <bk@raskon.ru>
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import logging

logger = logging.getLogger(__name__)

from Products.CMFCore.interfaces import IActionProvider, IActionsTool
import zope.interface
from AccessControl import ClassSecurityInfo
from Products.CMFCore import ActionsTool as CMFCore_ActionsToolModule
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.ActionProviderBase import ActionProviderBase
from Products.ERP5Type import Permissions
from zLOG import LOG, WARNING

CMFCore_ActionsTool = CMFCore_ActionsToolModule.ActionsTool

def _eventLessSetObject(container):
  _setObject = container._setObject
  return lambda *args, **kw: _setObject(suppress_events=True, *args, **kw)

def checkAndCreateActionToolBaseCategory(parent):
  if not parent.portal_categories.hasObject('action_type'):
    # Required to generate ActionInformation.getActionType accessor.
    import erp5
    action_type = getattr(erp5.portal_type, 'Base Category')('action_type')
    action_type.uid = None
    _eventLessSetObject(parent.portal_categories)(action_type.id, action_type)

class ActionsTool(BaseTool, ActionProviderBase, CMFCore_ActionsTool):
  """Provides a configurable registry of portal content types
  """
  id = "portal_actions"

  meta_type = 'ERP5 Actions Tool'
  portal_type = 'Actions Tool'
  allowed_types = ()

  zope.interface.implements(IActionsTool)

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def migrateNonProviders(self):
    portal_actions_path = '/'.join(self.getPhysicalPath())
    portal = self.getPortalObject()
    action_providers = list(self.action_providers)
    for provider_name in self.listActionProviders():
      provider = getattr(portal, provider_name)
      if (getattr(provider, '_actions', ()) and
              getattr(provider, 'listActionInfos', None) is None ):
        logger.info('migrating actions from %r to %r',
                    portal_actions_path, '/'.join(provider.getPhysicalPath()))
        for old_action in provider._actions:
          self._importOldAction(old_action)
        del provider._actions
      if (getattr(provider, 'listActionInfos', None) is None and
              getattr(provider, 'getActionListFor', None) is None and
            not (IActionProvider.providedBy(provider))):
        action_providers.remove(provider_name)
    self.action_providers = tuple(action_providers)

  security.declarePrivate('getActionListFor')
  def getActionListFor(self, ob=None):
    """Return all actions applicable to the object"""
    old_actions = self._actions or ()
    if old_actions:
      LOG('OldActionsTool', WARNING, "Converting portal_actions...")
      checkAndCreateActionToolBaseCategory(self)
      for action_info in old_actions:
        self._importOldAction(action_info)
      LOG('OldActionsTool', WARNING, "... portal_actions converted.")
      self._actions = ()
    if ob is not None:
      return (action.getCacheableAction() for action in self.objectValues())
    return ()

  def listFilteredActionsFor(self, object=None):
    """ List all actions available to the user.

    This patch removes inclusion of actions from the object itself.
    It was never used and now, it breaks objects inside Types Tool.

    It also checks for a new ERP5-only actions API (getActionListFor), but
    this API should be moved to listActionInfos() of each tool so as not to
    create duplicate code paths that are sources of bugs.

    Finally, this patch detects tools that are no longer action providers and
    invokes the migration of their actions to portal_actions
    """
    actions = []

    portal = self.getPortalObject()
    # Include actions from specific tools.
    for provider_name in self.listActionProviders():
      provider = getattr(portal, provider_name)
      if hasattr(provider, 'getActionListFor'):
        from Products.ERP5Type.Utils import createExpressionContext

        ec = createExpressionContext(object)
        actions.extend(action.cook(ec)
                       for action in provider.getActionListFor(object)
                       if action.test(ec))
      elif IActionProvider.providedBy(provider):
        actions.extend(provider.listActionInfos(object=object))
      else:
        # This should only be triggered once
        # We're in 2.12 and we need to migrate objects that are no longer
        # IActionProviders:
        self.migrateNonProviders()
        # Recompute from beginning
        return self.listFilteredActionsFor(object=object)

    actions.sort(key=lambda x: x.get('priority', 0))
    # Reorganize the actions by category.
    filtered_actions = {'user': [],
                        'folder': [],
                        'object': [],
                        'global': [],
                        'workflow': [],
                        }

    for action in actions:
      filtered_actions.setdefault(action['category'], []).append(action)

    return filtered_actions

# Change the CMFCore's ActionsTool to automatically migrate to ERP5Actions's
# ActionsTool
CMFCore_ActionsToolModule.ActionsTool = ActionsTool
