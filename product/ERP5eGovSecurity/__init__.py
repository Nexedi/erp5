##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#                  Fabien Morin <fabien@nexedi.com>
#                  Mohamadou Mbengue <mmbengue@gmail.com>
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
""" ERP5Security product initialization.
"""

from copy import deepcopy
from collections import defaultdict

from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from Products.PluggableAuthService.permissions import ManageGroups

import EGOVUserManager
import EGOVGroupManager
from Products.ERP5Security import ERP5UserFactory
from Products.ERP5Security import ERP5RoleManager


def mergedLocalRoles(object):
  """Returns a merging of object and its ancestors'
  __ac_local_roles__."""
  # Modified to take into account _getAcquireLocalRoles
  merged = defaultdict(list)
  object = aq_inner(object)
  while 1:
    local_role_dict = getattr(object, '__ac_local_roles__', None)
    if local_role_dict:
      if callable(local_role_dict):
        local_role_dict = local_role_dict() or {}
      for k, v in local_role_dict.iteritems():
        merged[k] += v
    # block acquisition
    if not getattr(object, '_getAcquireLocalRoles', lambda: True)():
      break
    parent = aq_parent(object)
    if parent is not None:
      object = aq_inner(parent)
      continue
    self = getattr(object, '__self__', None)
    if self is not None:
      object = aq_inner(self)
      continue
    break
  return deepcopy(merged)

registerMultiPlugin(EGOVUserManager.EGOVUserManager.meta_type)
registerMultiPlugin(EGOVGroupManager.EGOVGroupManager.meta_type)

def initialize(context):

    context.registerClass( EGOVUserManager.EGOVUserManager
                         , permission=ManageUsers
                         , constructors=(
                            EGOVUserManager.manage_addEGOVUserManagerForm,
                            EGOVUserManager.addEGOVUserManager, )
                         , visibility=None
                         , icon='www/portal.gif'
                         )

    context.registerClass( EGOVGroupManager.EGOVGroupManager
                         , permission=ManageGroups
                         , constructors=(
                            EGOVGroupManager.manage_addEGOVGroupManagerForm,
                            EGOVGroupManager.addEGOVGroupManager, )
                         , visibility=None
                         , icon='www/portal.gif'
                         )
