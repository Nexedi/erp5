##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Products.CMFCore.CatalogTool import IndexableObjectWrapper, CatalogTool

class PatchedIndexableObjectWrapper(IndexableObjectWrapper):

    def allowedRolesAndUsers(self):
        """
        Return a list of roles and users with View permission.
        Used by PortalCatalog to filter out items you're not allowed to see.
        """
        ob = self.__ob
        allowed = {}
        for r in rolesForPermissionOn('View', ob):
            allowed[r] = 1
        localroles = _mergedLocalRoles(ob)
        for user, roles in localroles.items():
            for role in roles:
                if allowed.has_key(role):
                    allowed['user:' + user] = 1
                # Added for ERP5 project by JP Smets
                if role != 'Owner': allowed['user:' + user + ':' + role] = 1
        if allowed.has_key('Owner'):
            del allowed['Owner']
        return list(allowed.keys())

IndexableObjectWrapper.allowedRolesAndUsers = PatchedIndexableObjectWrapper.allowedRolesAndUsers

class PatchedCatalogTool(CatalogTool):

    def searchResults(self, REQUEST=None, **kw):
        """
            Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        user = _getAuthenticatedUser(self)
        kw[ 'allowedRolesAndUsers' ] = self._listAllowedRolesAndUsers( user )

        # Patch for ERP5 by JP Smets in order
        # to implement worklists and search of local roles
        if kw.has_key('local_roles'):
          # Only consider local_roles if it is not empty
          if kw['local_roles'] != '' and  kw['local_roles'] != [] and  \
             kw['local_roles'] is not None:
            local_roles = kw['local_roles']
            # Turn it into a list if necessary according to ';' separator
            if type(local_roles) == type('a'):
              local_roles = local_roles.split(';')
            # Local roles now has precedence (since it comes from a WorkList)
            kw[ 'allowedRolesAndUsers' ] = []
            for role in local_roles:
                 kw[ 'allowedRolesAndUsers' ].append('user:%s:%s' % (user, role))

        if not _checkPermission( AccessInactivePortalContent, self ):
            base = aq_base( self )
            now = DateTime()
            if hasattr( base, 'addIndex' ):   # Zope 2.4 and above
                kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
                kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }
            else:                             # Zope 2.3
                kw[ 'effective'      ] = kw[ 'expires' ] = now
                kw[ 'effective_usage'] = 'range:max'
                kw[ 'expires_usage'  ] = 'range:min'

        return apply(ZCatalog.searchResults, (self, REQUEST), kw)

CatalogTool.searchResults = PatchedCatalogTool.searchResults