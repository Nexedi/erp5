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

from Products.CMFCore.ActionsTool import ActionsTool
try:
  from Products.CMFCore.interfaces import IActionProvider
  IActionProvider_providedBy = IActionProvider.providedBy
except ImportError:
  # XXX Do not initialize ZCML in unit tests on Zope 2.8 for the moment
  from Products.CMFCore.ActionsTool import IActionProvider
  IActionProvider_providedBy = IActionProvider.isImplementedBy

ActionsTool_listFilteredActionsFor = ActionsTool.listFilteredActionsFor

def listFilteredActionsFor(self, object=None):
    """ List all actions available to the user.

    This patch removes inclusion of actions from the object itself.
    It was never used and now, it breaks objects inside Types Tool.
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
        else:
            # for Action Providers written for CMF versions before 1.5
            actions.extend( self._listActionInfos(provider, object) )

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
