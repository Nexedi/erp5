# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2021 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Products.ERP5Type.mixin.expression import ExpressionMixin
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ERP5Type import Permissions

from Acquisition import aq_base
from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Core.Workflow import createExpressionContext, StateChangeInfo

class GuardableMixin(ExpressionMixin('guard_expression')):
  """
  Code of methods and functions taken from
  Products.DCWorkflow-2.2.4 > Guard.py
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.ManagePortal)

  @security.private
  def isGuarded(self):
    """
    Returns True if object has at least one of the guard securities set among:
      * expression
      * group
      * permission
      * role
    """
    return bool(self.getGuardExpression() or
                self.getGuardGroupList() or
                self.getGuardPermissionList() or
                self.getGuardRoleList())

  @security.private
  def checkGuard(self,
                 security_manager,
                 workflow,
                 current_object,
                 **kw):
    """
    Checks conditions in this guard. Original source code from DCWorkflow
    (Nexedi patch for proxy_roles)
    """
    user_roles = None

    def getRoles():
      stack = security_manager._context.stack
      if stack:
        proxy_roles = getattr(stack[-1], '_proxy_roles', None)
        if proxy_roles:
          return proxy_roles
      return security_manager.getUser().getRolesInContext(current_object)

    if workflow.isManagerBypass():
      # Possibly bypass.
      user_roles = getRoles()
      if 'Manager' in user_roles:
        return True
    guard_permission_list = self.getGuardPermissionList()
    if guard_permission_list:
      for permission in guard_permission_list:
        if _checkPermission(permission, current_object):
          break
      else:
        return False
    guard_role_list = self.getGuardRoleList()
    if guard_role_list:
      # Require at least one of the given roles.
      if user_roles is None:
        user_roles = getRoles()
      for role in guard_role_list:
        if role in user_roles:
          break
      else:
        return False
    guard_group_list = self.getGuardGroupList()
    if guard_group_list:
      # Require at least one of the specified groups.
      user = security_manager.getUser()
      base = aq_base(user)
      if hasattr(base, 'getGroupsInContext'):
        user_groups = user.getGroupsInContext(current_object)
      elif hasattr(base, 'getGroups' ):
        user_groups = user.getGroups()
      else:
        user_groups = ()
      for group in guard_group_list:
        if group in user_groups:
          break
      else:
        return False
    guard_expression = self.getGuardExpressionInstance()
    if guard_expression is not None:
      return guard_expression(
        createExpressionContext(StateChangeInfo(current_object,
                                                workflow,
                                                kwargs=kw)))
    return True

InitializeClass(GuardableMixin)
