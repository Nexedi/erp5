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

from Products.CMFCore.utils import *
from Products.CMFCore.utils import _verifyActionPermissions
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

security.declarePrivate('_getViewFor')
def CMFCoreUtils_getViewFor(obj, view='view'):
    warn('__call__() and view() methods using _getViewFor() as well as '
         '_getViewFor() itself are deprecated and will be removed in CMF 1.6. '
         'Bypass these methods by defining \'(Default)\' and \'view\' Method '
         'Aliases.',
         DeprecationWarning)
    ti = obj.getTypeInfo()

    if ti is not None:
        context = getActionContext( obj )
        actions = ti.listActions()
        for action in actions:
            if action.getId() == view or action.getCategory().endswith('_%s' % view):
                if _verifyActionPermissions(obj, action):
                  if action.testCondition(context):
                    target = action.action(context).strip()
                    if target.startswith('/'):
                        target = target[1:]
                    __traceback_info__ = ( ti.getId(), target )
                    return obj.restrictedTraverse( target )

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        for action in actions:
            if _verifyActionPermissions(obj, action):
              if action.testCondition(context):
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
