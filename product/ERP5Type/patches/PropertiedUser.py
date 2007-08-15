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

try:
  from Products.PluggableAuthService.PropertiedUser import PropertiedUser
  from Products.PluggableAuthService.PropertiedUser import\
                                              _what_not_even_god_should_do
except ImportError:
  PropertiedUser = None
  
def getRolesInContext( self, object ):

    """ Return the list of roles assigned to the user.

    o Include local roles assigned in context of the passed-in object.

    o Include *both* local roles assigned directly to us *and* those
      assigned to our groups.

    o Ripped off from AccessControl.User.BasicUser, which provides
      no other extension mechanism. :(
    """
    user_id = self.getId()
    # [ x.getId() for x in self.getGroups() ]
    group_ids = self.getGroups()

    principal_ids = list( group_ids )
    principal_ids.insert( 0, user_id )

    local ={} 
    object = aq_inner( object )

    while 1:

        local_roles = getattr( object, '__ac_local_roles__', None )

        if local_roles:

            if callable( local_roles ):
                local_roles = local_roles()

            dict = local_roles or {}

            for principal_id in principal_ids:
                for role in dict.get( principal_id, [] ):
                    local[ role ] = 1
                    
        # patch by Klaus for LocalRole blocking
        _getAcquireLocalRoles = getattr(object, '_getAcquireLocalRoles', None)
        if _getAcquireLocalRoles is not None:
            if not _getAcquireLocalRoles():
                break

        inner = aq_inner( object )
        parent = aq_parent( inner )

        if parent is not None:
            object = parent
            continue

        new = getattr( object, 'im_self', None )

        if new is not None:

            object = aq_inner( new )
            continue

        break
    
    return list( self.getRoles() ) + local.keys()

def allowed( self, object, object_roles=None ):

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

    # Check for a role match with the normal roles given to
    # the user, then with local roles only if necessary. We
    # want to avoid as much overhead as possible.
    user_roles = self.getRoles()
    for role in object_roles:
        if role in user_roles:
            if self._check_context(object):
                return 1
            return None

    # Still have not found a match, so check local roles. We do
    # this manually rather than call getRolesInContext so that
    # we can incur only the overhead required to find a match.
    inner_obj = aq_inner( object )
    user_id = self.getId()
    # [ x.getId() for x in self.getGroups() ]
    group_ids = self.getGroups()

    principal_ids = list( group_ids )
    principal_ids.insert( 0, user_id )

    while 1:

        local_roles = getattr( inner_obj, '__ac_local_roles__', None )

        if local_roles:

            if callable( local_roles ):
                local_roles = local_roles()

            dict = local_roles or {}

            for principal_id in principal_ids:

                local_roles = dict.get( principal_id, [] )

                for role in object_roles:

                    if role in local_roles:

                        if self._check_context( object ):
                            return 1

                        return 0
                    
        # patch by Klaus for LocalRole blocking
        _getAcquireLocalRoles = getattr(object, '_getAcquireLocalRoles', None)
        if _getAcquireLocalRoles is not None:
            if not _getAcquireLocalRoles():
                break

        inner = aq_inner( inner_obj )
        parent = aq_parent( inner )

        if parent is not None:
            inner_obj = parent
            continue

        new = getattr( inner_obj, 'im_self', None )

        if new is not None:
            inner_obj = aq_inner( new )
            continue

        break

    return None

if PropertiedUser is not None:
  PropertiedUser.getRolesInContext = getRolesInContext
  PropertiedUser.allowed = allowed
