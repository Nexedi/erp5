##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# monkeypatch to have role mathods call reindex

# make sure NuxUserGroups monkeypatches RoleManager first
try:
  import NuxUserGroups
except ImportError:
  pass

from AccessControl.Role import RoleManager

# Security and catalog reindexing triggers
def manage_addLocalRoles(self, userid, roles, REQUEST=None):
  "reindex after role update"
  RoleManager.old_manage_addLocalRoles(self, userid, roles, REQUEST=REQUEST)
  reindex_method = getattr(self, 'recursiveReindexObject', None)
  if reindex_method is not None: reindex_method()

def manage_setLocalRoles(self, userid, roles, REQUEST=None):
  "reindex after role update"
  RoleManager.old_manage_setLocalRoles(self, userid, roles, REQUEST=REQUEST)
  reindex_method = getattr(self, 'recursiveReindexObject', None)
  if reindex_method is not None: reindex_method()

def manage_delLocalRoles(self, userid, REQUEST=None):
  "reindex after role update"
  RoleManager.old_manage_delLocalRoles(self, userid, REQUEST=REQUEST)
  reindex_method = getattr(self, 'recursiveReindexObject', None)
  if reindex_method is not None: reindex_method()

def manage_addLocalGroupRoles(self, groupid, roles, REQUEST=None):
  "reindex after role update"
  RoleManager.old_manage_addLocalGroupRoles(self, groupid, roles, REQUEST=REQUEST)
  reindex_method = getattr(self, 'recursiveReindexObject', None)
  if reindex_method is not None: reindex_method()

def manage_setLocalGroupRoles(self, groupid, roles, REQUEST=None):
  "reindex after role update"
  RoleManager.old_manage_setLocalGroupRoles(self, groupid, roles, REQUEST=REQUEST)
  reindex_method = getattr(self, 'recursiveReindexObject', None)
  if reindex_method is not None: reindex_method()

def manage_delLocalGroupRoles(self, groupids, REQUEST=None):
  "reindex after role update"
  RoleManager.old_manage_delLocalGroupRoles(self, groupids, REQUEST=REQUEST)
  reindex_method = getattr(self, 'recursiveReindexObject', None)
  if reindex_method is not None: reindex_method()

RoleManager.old_manage_addLocalRoles = RoleManager.manage_addLocalRoles
RoleManager.manage_addLocalRoles = manage_addLocalRoles
RoleManager.old_manage_setLocalRoles = RoleManager.manage_setLocalRoles
RoleManager.manage_setLocalRoles = manage_setLocalRoles
RoleManager.old_manage_delLocalRoles = RoleManager.manage_delLocalRoles
RoleManager.manage_delLocalRoles = manage_delLocalRoles

if getattr(RoleManager, 'manage_addLocalGroupRoles', None) is not None:
  RoleManager.old_manage_addLocalGroupRoles = RoleManager.manage_addLocalGroupRoles
  RoleManager.manage_addLocalGroupRoles = manage_addLocalGroupRoles
  RoleManager.old_manage_setLocalGroupRoles = RoleManager.manage_setLocalGroupRoles
  RoleManager.manage_setLocalGroupRoles = manage_setLocalGroupRoles
  RoleManager.old_manage_delLocalGroupRoles = RoleManager.manage_delLocalGroupRoles
  RoleManager.manage_delLocalGroupRoles = manage_delLocalGroupRoles

