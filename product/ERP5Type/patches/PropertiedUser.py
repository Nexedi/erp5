##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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

# Locale roles acquisition patch for PAS

from Acquisition import aq_inner, aq_parent
from App.config import getConfiguration
try:
  from Products.PluggableAuthService.PropertiedUser import PropertiedUser
  from Products.PluggableAuthService.PropertiedUser import\
                                              _what_not_even_god_should_do
except ImportError:
  PropertiedUser = None

TRUE_LAMBDA = lambda: True
DEVELOPER_ROLE_ID = 'Developer'

def getRolesInContext(self, object):

    """ Return the list of roles assigned to the user.

    o Include local roles assigned in context of the passed-in object.

    o Include *both* local roles assigned directly to us *and* those
      assigned to our groups.

    o Ripped off from AccessControl.User.BasicUser, which provides
      no other extension mechanism. :(
    """
    principal_id_list = [self.getId()]
    principal_id_list.extend(self.getGroups())
    result = set()
    object = aq_inner(object)
    while 1:
        local_role_dict = getattr(object, '__ac_local_roles__', None)
        if local_role_dict is not None:
            if callable(local_role_dict):
                local_role_dict = local_role_dict() or {}
            for principal_id in principal_id_list:
                for role in local_role_dict.get(principal_id, ()):
                    result.add(role)
        if getattr(object, '_getAcquireLocalRoles', TRUE_LAMBDA)():
            parent = aq_parent(aq_inner(object))
            if parent is not None:
                object = parent
                continue
            new = getattr(object, '__self__', None)
            if new is not None:
                object = aq_inner(new)
                continue
        break
    # Patched: Developer role should never be available as local role
    result.discard(DEVELOPER_ROLE_ID)
    result.update(self.getRoles())
    return list(result)

def allowed(self, object, object_roles=None):
    """ Check whether the user has access to object.

    o The user must have one of the roles in object_roles to allow access.

    o Include *both* local roles assigned directly to us *and* those
      assigned to our groups.

    o Ripped off from AccessControl.User.BasicUser, which provides
      no other extension mechanism. :(
    """
    if object_roles is _what_not_even_god_should_do:
        return 0

    # Short-circuit the common case of anonymous access.
    if object_roles is None or 'Anonymous' in object_roles:
        return 1

    object_roles = set(object_roles)

    # Provide short-cut access if object is protected by 'Authenticated'
    # role and user is not nobody
    if 'Authenticated' in object_roles and (
        self.getUserName() != 'Anonymous User'):
        return 1

    # Check for ancient role data up front, convert if found.
    # This should almost never happen, and should probably be
    # deprecated at some point.
    if 'Shared' in object_roles:
        object_roles = self._shared_roles(object)
        if object_roles is None or 'Anonymous' in object_roles:
            return 1

    # Check global roles.
    if object_roles.intersection(self.getRoles()):
        return self._check_context(object)
    # Do not match Developer as a local role.
    object_roles.discard(DEVELOPER_ROLE_ID)

    check_context = self._check_context
    # Check local roles.
    inner_obj = aq_inner(object)
    principal_id_list = [self.getId()]
    principal_id_list.extend(self.getGroups())
    while 1:
      local_role_dict = getattr(inner_obj, '__ac_local_roles__', None)
      if local_role_dict is not None:
        if callable(local_role_dict):
          local_role_dict = local_role_dict() or {}
        for principal_id in principal_id_list:
          for role in object_roles.intersection(
            local_role_dict.get(principal_id, ()),
          ):
            return int(bool(check_context(object)))
      if getattr(inner_obj, '_getAcquireLocalRoles', TRUE_LAMBDA)():
        parent = aq_parent(aq_inner(inner_obj))
        if parent is not None:
          inner_obj = parent
          continue
        new = getattr(inner_obj, '__self__', None)
        if new is not None:
          inner_obj = aq_inner(new)
          continue
      break
    return None

orig_PropertiedUser__init__ = getattr(PropertiedUser, '__init__', None)
def PropertiedUser__init__(self, id, login=None):
    orig_PropertiedUser__init__(self, id, login)
    if id in getattr(
        getattr(
            getConfiguration(),
            'product_config',
            {},
        ).get('erp5'),
        'developer_list',
        (),
    ):
        self._roles[DEVELOPER_ROLE_ID] = 1

orig_PropertiedUser__addRoles = getattr(PropertiedUser, '_addRoles', None)
def PropertiedUser__addRoles(self, roles=()):
    orig_PropertiedUser__addRoles(self, (x for x in roles if x != DEVELOPER_ROLE_ID))

if PropertiedUser is not None:
    PropertiedUser.getRolesInContext = getRolesInContext
    PropertiedUser.allowed = allowed
    PropertiedUser.__init__ = PropertiedUser__init__
    PropertiedUser._addRoles = PropertiedUser__addRoles
