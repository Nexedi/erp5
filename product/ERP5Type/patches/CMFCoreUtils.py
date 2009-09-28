##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from warnings import warn
from Products.CMFCore.exceptions import AccessControl_Unauthorized, NotFound
from Products.CMFCore.utils import getActionContext
from Products.CMFCore.utils import _verifyActionPermissions
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore import PortalContent

from zLOG import LOG

"""
  This patch is based on Products/CMFCore/utils.py file from CMF 1.5.0 package.
  Please update the following file if you update CMF to greater version.
  The modifications in this method are:
    * new filter on default action (= "action.getCategory().endswith('_%s' % view)" statement)
    * new test on action condition (= "action.testCondition(context)" statement)
  This method was patched to let CMF choose between several default actions according conditions.
"""

def CMFCoreUtils_getViewFor(obj, view='view'):
    warn('__call__() and view() methods using _getViewFor() as well as '
         '_getViewFor() itself are deprecated and will be removed in CMF 1.6. '
         'Bypass these methods by defining \'(Default)\' and \'view\' Method '
         'Aliases.',
         DeprecationWarning)
    ti = obj.getTypeInfo()

    if ti is not None:
        context = getActionContext( obj )
        test_context = getExprContext(obj, obj) # Patch 1: mimic _listActionInfos in ActionsTool
        actions = ti.listActions()
        for action in actions:
            # portal_types hack
            action_type = action.getActionType()
            reference = getattr(action, 'reference', None) or action.id
            if reference == view or action_type.endswith('_%s' % view): # Patch 2: consider anything ending by _view
                if _verifyActionPermissions(obj, action):
                  if action.isVisible() and action.testCondition(test_context): # Patch 3: test actions
                    target = action.action(context).strip()
                    if target.startswith('/'):
                        target = target[1:]
                    __traceback_info__ = ( ti.getId(), target )
                    return obj.restrictedTraverse( target )

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        for action in actions:
            if _verifyActionPermissions(obj, action):
              if action.visible and action.testCondition(test_context): # Patch 3: test actions
                target = action.action(context).strip()
                if target.startswith('/'):
                    target = target[1:]
                __traceback_info__ = ( ti.getId(), target )
                return obj.restrictedTraverse( target )
        raise AccessControl_Unauthorized( 'No accessible views available for '
                                    '%s' % '/'.join( obj.getPhysicalPath() ) )
    else:
        raise NotFound('Cannot find default view for "%s"' %
                            '/'.join(obj.getPhysicalPath()))

PortalContent._getViewFor = CMFCoreUtils_getViewFor
