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
import transaction
from Acquisition import aq_parent

logger = logging.getLogger(__name__)

from Products.CMFCore.ActionsTool import ActionsTool
try:
  from Products.CMFCore.interfaces import IActionProvider
  IActionProvider_providedBy = IActionProvider.providedBy
except ImportError:
  # XXX Do not initialize ZCML in unit tests on Zope 2.8 for the moment
  from Products.CMFCore.ActionsTool import IActionProvider
  IActionProvider_providedBy = IActionProvider.isImplementedBy

def migrateNonProviders(portal_actions):
  portal_actions_path = '/'.join(portal_actions.getPhysicalPath())
  root = portal_actions.getPhysicalRoot()
  # Discard all changes so far, we'll restart the request later so no changes
  # are lost.
  root._p_jar.sync()
  txn = transaction.get()

  portal_actions = root.unrestrictedTraverse(portal_actions_path)
  portal = aq_parent(portal_actions)
  action_providers = list(portal_actions.action_providers)
  for provider_name in portal_actions.listActionProviders():
    provider = getattr(portal, provider_name)
    if ( getattr(provider, '_actions', ()) and
         getattr(provider, 'listActionInfos', None) is None ):
      msg = ('migrating actions from %r to %r' % 
             (portal_actions_path, '/'.join(provider.getPhysicalPath())))
      logger.warning(msg)
      txn.note(msg)
      portal_actions._actions += provider._actions
      del provider._actions
      action_providers.remove(provider_name)
  portal_actions.action_providers = tuple(action_providers)
  
  txn.note('Migrated actions from non IActionProviders to portal_actions')
  txn.commit()
  # restart the transaction with actions already migrated
  from ZODB.POSException import ConflictError
  raise ConflictError('Action Migration Completed, please restart request.')

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
        elif IActionProvider_providedBy(provider):
            actions.extend( provider.listActionInfos(object=object) )
        elif getattr(provider, '_listActionInfos', None) is not None:
            # BACK: drop this clause and the 'else' clause below when we
            # drop CMF 1.5

            # for Action Providers written for CMF versions before 1.5
            actions.extend( self._listActionInfos(provider, object) )
        else:
            # We're in 2.12 and we need to migrate objects that are no longer
            # IActionProviders:
            migrateNonProviders(self)

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
