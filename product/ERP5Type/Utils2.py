##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solane <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
#
# Based on: utils.py in CMFCore
#
##############################################################################

from AccessControl import ModuleSecurityInfo
from Products.CMFCore.utils import _verifyActionPermissions, getActionContext

security = ModuleSecurityInfo( 'Products.ERP5.UI.Utils' )

security.declarePrivate('_getViewFor')
def _getListFor(obj, view='list'):
    ti = obj.getTypeInfo()

    if ti is not None:

        context = getActionContext( obj )
        actions = ti.listActions()

        for action in actions:
            if action.getId() == view:
                if _verifyActionPermissions( obj, action ):
                    target = action.action(context).strip()
                    if target.startswith('/'):
                        target = target[1:]
                    __traceback_info__ = ( ti.getId(), target )
                    return obj.restrictedTraverse( target )

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        for action in actions:
            if _verifyActionPermissions(obj, action):
                target = action.action(context).strip()
                if target.startswith('/'):
                    target = target[1:]
                __traceback_info__ = ( ti.getId(), target )
                return obj.restrictedTraverse( target )

        raise 'Unauthorized', ('No accessible views available for %s' %
                               '/'.join(obj.getPhysicalPath()))
    else:
        raise 'Not Found', ('Cannot find default view for "%s"' %
                            '/'.join(obj.getPhysicalPath()))

