##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import logging

logger = logging.getLogger(__name__)

from Products.CMFCore.ActionsTool import ActionsTool
from Products.CMFCore.interfaces import IActionProvider

def migrateNonProviders(portal_actions):
  portal_actions_path = '/'.join(portal_actions.getPhysicalPath())
  portal = portal_actions.getPortalObject()
  action_providers = list(portal_actions.action_providers)
  for provider_name in portal_actions.listActionProviders():
    provider = getattr(portal, provider_name)
    if ( getattr(provider, '_actions', ()) and
         getattr(provider, 'listActionInfos', None) is None ):
      logger.info('migrating actions from %r to %r',
         portal_actions_path, '/'.join(provider.getPhysicalPath()))
      portal_actions._actions += provider._actions
      del provider._actions
    if (getattr(provider, 'listActionInfos', None) is None and
        getattr(provider, 'getActionListFor', None) is None and
        not(IActionProvider.providedBy(provider))):
      action_providers.remove(provider_name)
  portal_actions.action_providers = tuple(action_providers)

ActionsTool_listFilteredActionsFor = ActionsTool.listFilteredActionsFor

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

    # Include actions from specific tools.
    for provider_name in self.listActionProviders():
        provider = getattr(self, provider_name)
        if hasattr(provider, 'getActionListFor'):
            from Products.ERP5Type.Utils import createExpressionContext
            ec = createExpressionContext(object)
            actions.extend(action.cook(ec)
                           for action in provider.getActionListFor(object)
                           if action.test(ec))
        elif IActionProvider.providedBy(provider):
            actions.extend( provider.listActionInfos(object=object) )
        else:
            # This should only be triggered once
            # We're in 2.12 and we need to migrate objects that are no longer
            # IActionProviders:
            migrateNonProviders(self)
            # Recompute from beginning
            return self.listFilteredActionsFor(object=object)

    actions.sort(key=lambda x:x.get('priority', 0))
    # Reorganize the actions by category.
    filtered_actions={'user':[],
                      'folder':[],
                      'object':[],
                      'global':[],
                      'workflow':[],
                      }

    for action in actions:
        filtered_actions.setdefault(action['category'], []).append(action)

    return filtered_actions

ActionsTool.listFilteredActionsFor = listFilteredActionsFor


def reorderActions(self, REQUEST=None):
  """Reorder actions according to their priorities."""
  new_actions = self._cloneActions()
  new_actions.sort(key=lambda x: x.getPriority())
  self._actions = tuple( new_actions )

  if REQUEST is not None:
    return self.manage_editActionsForm(REQUEST,
        manage_tabs_message='Actions reordered.')

ActionsTool.reorderActions = reorderActions
