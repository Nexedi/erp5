from cgi import escape

from AccessControl.SecurityInfo import ClassSecurityInfo
from Acquisition import Explicit
from Acquisition import aq_base
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from Persistence import Persistent

from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type import Permissions

from Products.DCWorkflow.Expression import StateChangeInfo
from Products.DCWorkflow.Expression import createExprContext
from Products.DCWorkflow.utils import _dtmldir


class GuardableMixin(object):
  '''
  code of methods and functions taken from
  Products.DCWorkflow-2.2.4 > Guard.py
  '''

  guard_expression = Expression('')
  guard_group = ()
  guard_permission = ()
  guard_role = ()

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.ManagePortal)

  def isGuarded(self):
    # Returns True if object has at least one of the guard securities set among:
    #  * expression
    #  * group
    #  * permission
    #  * role
    return self.guard_expression or self.guard_group or \
    self.guard_permission or self.guard_role

  def checkGuard(self, security_manager, workflow, current_object, check_roles=True, **kw):
    # Checks conditions in this guard.
    # original source code from DCWorkflow (Nexedi patched version for use of
    # proxy_roles)
    user_roles = None

    def getRoles():
      stack = security_manager._context.stack
      if stack:
        proxy_roles = getattr(stack[-1], '_proxy_roles', None)
        if proxy_roles:
          return proxy_roles
      return security_manager.getUser().getRolesInContext(current_object)

    if workflow.manager_bypass:
      # Possibly bypass.
      user_roles = getRoles()
      if 'Manager' in user_roles:
        return True
    if self.guard_permission:
      for permission in self.guard_permission:
        if _checkPermission(permission, current_object):
          break
      else:
        return False
    if check_roles and self.guard_role:
      # Require at least one of the given roles.
      if user_roles is None:
        user_roles = getRoles()
      for role in self.guard_role:
        if role in user_roles:
          break
      else:
        return False
    if self.guard_group:
      # Require at least one of the specified groups.
      user = security_manager.getUser()
      base = aq_base(user)
      if hasattr(base, 'getGroupsInContext'):
        user_groups = user.getGroupsInContext(current_object)
      elif hasattr(base, 'getGroups' ):
        user_groups = user.getGroups()
      else:
        user_groups = ()
      for group in self.guard_group:
        if group in user_groups:
          break
      else:
        return False
    if self.guard_expression and self.guard_expression.text:
      expression_context = createExprContext(StateChangeInfo(current_object,
                                                             workflow,
                                                             kwargs=kw))
      if not self.guard_expression(expression_context):
        return False
    return True

  # Same as WorkflowVariable.variable_expression
  def _setGuardExpression(self, text):
    if text:
      self.guard_expression = Expression(text)
    else:
      self.guard_expression = None

  def _getGuardExpression(self):
    if self.guard_expression is None:
      return Expression('')
    return self.guard_expression
