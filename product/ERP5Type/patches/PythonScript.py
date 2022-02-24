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
from Products.DCWorkflow.Guard import Guard
from Products.PythonScripts.PythonScript import PythonScript
from App.special_dtml import DTMLFile
from .. import _dtmldir
from . import PatchClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.class_init import InitializeClass
from AccessControl.PermissionRole import rolesForPermissionOn
from OFS.misc_ import p_
from App.ImageFile import ImageFile
from Acquisition import aq_base, aq_parent
from zExceptions import Forbidden

### Guards

_guard_manage_options = (
  {
    'label':'Guard',
    'action':'manage_guardForm',
  },
)

_guard_form = DTMLFile(
  'editGuardForm', _dtmldir)

def manage_guardForm(self, REQUEST, manage_tabs_message=None):
  '''
  '''
  return self._guard_form(REQUEST,
                          management_view='Guard',
                          manage_tabs_message=manage_tabs_message,
    )

def manage_setGuard(self, props=None, REQUEST=None):
  '''
  '''
  g = Guard()
  if g.changeFromProperties(props or REQUEST):
    guard = self.guard
    if guard is None:
      self.guard = g
    else:
      guard._p_activate()
      if guard.__dict__ != g.__dict__:
        guard.__dict__.clear()
        guard.__dict__.update(g.__dict__)
        guard._p_changed = 1
  else:
    try:
      del self.guard
    except AttributeError:
      pass
  if REQUEST is not None:
    return self.manage_guardForm(REQUEST, 'Properties changed.')

def getGuard(self):
  guard = self.guard
  if guard is None:
    return Guard().__of__(self)  # Create a temporary guard.
  return guard

def getRoles(ob):
  sm = getSecurityManager()
  stack = sm._context.stack
  if stack:
    proxy_roles = getattr(stack[-1], '_proxy_roles', None)
    if proxy_roles:
      return set(proxy_roles)
  return set(sm.getUser().getRolesInContext(ob))

def _checkGuard(guard, ob):
  # returns 1 if guard passes against ob, else 0.
  # TODO : implement TALES evaluation by defining an appropriate
  # context.
  if guard.permissions:
    # Require at least one role for required roles for the given permission.
    u_roles = getRoles(ob)
    for p in guard.permissions:
      if not u_roles.isdisjoint(rolesForPermissionOn(p, ob)):
        break
    else:
      return 0
  else:
    u_roles = None
  if guard.roles:
    # Require at least one of the given roles.
    if u_roles is None:
      u_roles = getRoles(ob)
    if u_roles.isdisjoint(guard.roles):
      return 0
  if guard.groups:
    # Require at least one of the specified groups.
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

def checkGuard(aq_parent=aq_parent, _checkGuard=_checkGuard):
  def checkGuard(self, _exec=False):
    guard = self.guard
    if guard is None or _checkGuard(guard, aq_parent(self)):
      return 1
    if _exec:
      raise Forbidden('Calling %s %s is denied by Guard.'
                      % (self.meta_type, self.id))
  return checkGuard
checkGuard = checkGuard()

def addGuard(cls, set_permission):
  security = cls.security

  cls.guard = None
  cls.getGuard = getGuard
  cls.checkGuard = checkGuard

  cls.manage_options += _guard_manage_options
  cls._guard_form = _guard_form

  security.declareProtected('View management screens', 'manage_guardForm')
  cls.manage_guardForm = manage_guardForm

  security.declareProtected(set_permission, 'manage_setGuard')
  cls.manage_setGuard = manage_setGuard

###

class _(PatchClass(PythonScript)):

  security = ClassSecurityInfo()

  # Add proxy role icon in ZMI

  def om_icons(self):
    """Return a list of icon URLs to be displayed by an ObjectManager"""
    if self._proxy_roles:
      return {'path': 'p_/PythonScript_ProxyRole_icon',
              'alt': 'Proxy Roled Python Script',
              'title': 'This script has proxy role.'},
    return {'path': 'misc_/PythonScripts/pyscript.gif',
            'alt': self.meta_type, 'title': self.meta_type},

  p_.PythonScript_ProxyRole_icon = \
    ImageFile('pyscript_proxyrole.gif', globals())


  # Guards

  def __call__(self, *args, **kw):
    '''Calls the script.'''
    self.checkGuard(True) # patch
    return self._orig_bindAndExec(args, kw, None)

  security.declarePublic("render")
  render = __call__

  # For __render_with_namespace__ (we prefer to monkey-patch __call__
  # because it's called more often, and this makes debugging easier)
  _orig_bindAndExec = PythonScript._bindAndExec
  def _bindAndExec(self, args, kw, caller_namespace):
    return self(*args, **kw) # caller_namespace not used by PythonScript

  ## WITH_LEGACY_WORKFLOW
  def getReference(self):
    return self.id
  # Following methods are necessary for Workflow showAsXML() function
  def getBody(self):
    return self._body
  def getParams(self):
    return self._params
  def getProxyRole(self):
    return self._proxy_roles

addGuard(PythonScript, 'Change Python Scripts')

InitializeClass(PythonScript)
