##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2012 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from AccessControl.User import BasicUser

BasicUser_allowed = BasicUser.allowed
def allowed(self, object, object_roles=None):
  """
  Check if the user has Developer role which allows to modify ZODB source code
  and remove it, as it should never be acquired anyhow, before calling the
  original method
  """
  # XXX-arnau: copy/paste (PropertiedUser)
  if object_roles is not None:
    object_roles = set(object_roles)
    if 'Developer' in object_roles:
      object_roles.remove('Developer')
      product_config = getattr(getConfiguration(), 'product_config', None)
      if product_config:
        config = product_config.get('erp5', None)
        if config and self.getId() in config.developer_list:
          return 1

  return BasicUser_allowed(self, object, object_roles)

BasicUser.allowed = allowed

from App.config import getConfiguration
from AccessControl.User import SimpleUser

SimpleUser_getRoles = SimpleUser.getRoles
def getRoles(self):
  """
  Add Developer Role if the user has been explicitely set as Developer in Zope
  configuration file
  """
  role_tuple = SimpleUser_getRoles(self)
  if role_tuple:
    product_config = getattr(getConfiguration(), 'product_config', None)
    if product_config:
      config = product_config.get('erp5', None)
      if config:
        role_set = set(role_tuple)
        user_id = self.getId()
        if config and user_id in config.developer_list:
          role_set.add('Developer')
        elif user_id in role_set:
          role_set.remove('Developer')

        return role_set

  return role_tuple

SimpleUser.getRoles = getRoles

SimpleUser_getRolesInContext = SimpleUser.getRolesInContext
def getRolesInContext(self, object):
  """
  Return the list of roles assigned to the user, including local roles
  assigned in context of the passed in object.
  """
  userid=self.getId()
  roles=self.getRoles()
  local={}
  object=getattr(object, 'aq_inner', object)
  while 1:
    local_roles = getattr(object, '__ac_local_roles__', None)
    if local_roles:
      if callable(local_roles):
        local_roles=local_roles()
      dict=local_roles or {}
      for r in dict.get(userid, []):
        local[r]=1
    inner = getattr(object, 'aq_inner', object)
    parent = getattr(inner, '__parent__', None)
    if parent is not None:
      object = parent
      continue
    if hasattr(object, 'im_self'):
      object=object.im_self
      object=getattr(object, 'aq_inner', object)
      continue
    break

  # Patched: Developer role should not never be available as local role
  local.pop('Developer', None)
  roles=list(roles) + local.keys()
  return roles

SimpleUser.getRolesInContext = getRolesInContext
