##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
from Products.CMFCore.utils import _checkPermission
from Products.DCWorkflow.Guard import Guard
from Products.PythonScripts.PythonScript import PythonScript
from App.special_dtml import DTMLFile
from Products.ERP5Type import _dtmldir
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.class_init import InitializeClass
from OFS.misc_ import p_
from App.ImageFile import ImageFile
from Acquisition import aq_base, aq_parent
from zExceptions import Forbidden

security = ClassSecurityInfo()
PythonScript.security = security

def haveProxyRole(self):
  """if a script has proxy role, return True"""
  return bool(self._proxy_roles)

def om_icons(self):
  """Return a list of icon URLs to be displayed by an ObjectManager"""
  icons = ({'path': 'misc_/PythonScripts/pyscript.gif',
            'alt': self.meta_type, 'title': self.meta_type},)
  if self.haveProxyRole():
    icons = ({'path': 'p_/PythonScript_ProxyRole_icon',
              'alt': 'Proxy Roled Python Script',
              'title': 'This script has proxy role.'},)
  return icons

pyscript_proxyrole = ImageFile('pyscript_proxyrole.gif', globals())

#
# Add proxy role icon in ZMI
#
security.declarePrivate('haveProxyRole')
PythonScript.haveProxyRole = haveProxyRole

PythonScript.om_icons = om_icons
p_.PythonScript_ProxyRole_icon = pyscript_proxyrole


# Patch for displaying textearea in full window instead of
# remembering a quantity of lines to display in a cookie
manage_editForm = DTMLFile("pyScriptEdit", _dtmldir)
manage_editForm._setName('manage_editForm')
PythonScript.ZPythonScriptHTML_editForm = manage_editForm
PythonScript.manage_editForm = manage_editForm
PythonScript.manage = manage_editForm
PythonScript.manage_main = manage_editForm
PythonScript.manage_editDocument = manage_editForm
PythonScript.manage_editForm = manage_editForm

_guard_manage_options = (
  {
    'label':'Guard',
    'action':'manage_guardForm',
  },
)
PythonScript.manage_options += _guard_manage_options

_guard_form = DTMLFile(
  'editGuardForm', _dtmldir)
PythonScript._guard_form = _guard_form

def manage_guardForm(self, REQUEST, manage_tabs_message=None):
  '''
  '''
  return self._guard_form(REQUEST,
                          management_view='Guard',
                          manage_tabs_message=manage_tabs_message,
    )
PythonScript.manage_guardForm = manage_guardForm
security.declareProtected('View management screens', 'manage_guardForm')

def manage_setGuard(self, props=None, REQUEST=None):
  '''
  '''
  g = Guard()
  if g.changeFromProperties(props or REQUEST):
    self.guard = g
  else:
    self.guard = None
  if REQUEST is not None:
    return self.manage_guardForm(REQUEST, 'Properties changed.')
PythonScript.manage_setGuard = manage_setGuard
security.declareProtected('Change Python Scripts', 'manage_setGuard')

def getGuard(self):
  guard = getattr(self, 'guard', None)
  if guard is not None:
    return guard
  else:
    return Guard().__of__(self)  # Create a temporary guard.
PythonScript.getGuard = getGuard

def checkGuard(guard, ob):
  # returns 1 if guard passes against ob, else 0.
  # TODO : implement TALES evaluation by defining an appropriate
  # context.
  sm = None
  if guard.permissions:
    for p in guard.permissions:
      if _checkPermission(p, ob):
        break
      else:
        return 0
  if guard.roles:
    if sm is None:
      sm = getSecurityManager()
      u = sm.getUser()
    def getRoles():
      stack = sm._context.stack
      if stack and len(stack) > 1:
        eo = stack[-2] # -1 is the current script.
        proxy_roles = getattr(eo, '_proxy_roles', None)
        if proxy_roles:
          return proxy_roles
      return u.getRolesInContext(ob)
    # Require at least one of the given roles.
    u_roles = getRoles()
    for role in guard.roles:
      if role in u_roles:
        break
    else:
      return 0
  if guard.groups:
    # Require at least one of the specified groups.
    if sm is None:
      sm = getSecurityManager()
      u = sm.getUser()
    b = aq_base( u )
    if hasattr( b, 'getGroupsInContext' ):
      u_groups = u.getGroupsInContext( ob )
    elif hasattr( b, 'getGroups' ):
      u_groups = u.getGroups()
    else:
      u_groups = ()
    for group in guard.groups:
      if group in u_groups:
        break
    else:
      return 0
  return 1

PythonScript_exec = PythonScript._exec
def _exec(self, *args):
  # PATCH BEGIN : check guard against context, if guard exists.
  guard = getattr(self, 'guard', None)
  if guard is not None:
    if not checkGuard(guard, aq_parent(self)):
      raise Forbidden, 'Calling %s %s is denied by Guard.' % (self.meta_type, self.id)
  # PATCH END
  return PythonScript_exec(self, *args)
PythonScript._exec = _exec

InitializeClass(PythonScript)
