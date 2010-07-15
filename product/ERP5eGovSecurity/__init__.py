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
  merged = {}
  object = getattr(object, 'aq_inner', object)
  while 1:
    if getattr(object, '__ac_local_roles__', None) is not None:
      roles = object.__ac_local_roles__ or {}
      if callable(roles): roles = roles()
      for k, v in roles.iteritems():
        merged.setdefault(k, []).extend(v)
    # block acquisition
    if getattr(object, '_getAcquireLocalRoles', None) is not None:
      if not object._getAcquireLocalRoles() is not None:
        break
    if getattr(object, 'aq_parent', None) is not None:
      object = object.aq_parent
      object = getattr(object, 'aq_inner', object)
      continue
    if getattr(object, 'im_self', None) is not None:
      object = object.im_self
      object = getattr(object, 'aq_inner', object)
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
