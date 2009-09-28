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
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore import PortalContent

from zLOG import LOG

"""
  This patch is based on Products/CMFCore/utils.py file from CMF 1.5.0 package.
  Please update the following file if you update CMF to greater version.
  The modifications in this method are:
    * new filter on default action (= ".endswith('_%s' % view)" statement)
    * use action API to check its visibility in the context
  This method was patched to let CMF choose between several default actions according conditions.
"""

def CMFCoreUtils_getViewFor(obj, view='view'):
    warn('__call__() and view() methods using _getViewFor() as well as '
         '_getViewFor() itself are deprecated and will be removed in CMF 1.6. '
         'Bypass these methods by defining \'(Default)\' and \'view\' Method '
         'Aliases.',
         DeprecationWarning)
    ti = obj.getTypeInfo()
    if ti is None:
      raise NotFound('Cannot find default view for %r' % obj.getPath())

    context = getActionContext(obj)
    ec = getExprContext(obj, obj)
    best_action = (), None
    for action in ti.getFilteredActionListFor(obj):
      if action.getReference() == view:
        if action.test(ec):
          break
      else:
        # In case that "view" action is not present or not allowed,
        # find something that's allowed.
        index = (action.getActionType().endswith('_' + view),
                 -action.getFloatIndex())
        if best_action[0] < index and action.test(ec):
          best_action = index, action
    else:
      action = best_action[1]
      if action is None:
        raise AccessControl_Unauthorized('No accessible views available for %r'
                                         % obj.getPath())

    target = action.getActionUrl(context).strip()
    if target.startswith('/'):
        target = target[1:]
    __traceback_info__ = ti.getId(), target
    return obj.restrictedTraverse(target)

PortalContent._getViewFor = CMFCoreUtils_getViewFor
