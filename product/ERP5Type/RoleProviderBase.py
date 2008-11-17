##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Implement a shared base for tools which provide roles.

$Id$
"""

from Globals import DTMLFile, InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import _dtmldir

from RoleInformation import RoleInformation
from Permissions import ManagePortal

from zLOG import LOG

#from interfaces.portal_roles import RoleProvider as IRoleProvider


class RoleProviderBase:
    """ Provide RoleTabs and management methods for RoleProviders
    """

    #__implements__ = IRoleProvider

    security = ClassSecurityInfo()

    _roles = ()

    _roles_form = DTMLFile( 'editToolsRoles', _dtmldir )

    manage_options = ( { 'label' : 'Roles'
                       , 'action' : 'manage_editRolesForm'
                       }
                     ,
                     )

    #
    #   RoleProvider interface
    #
    security.declarePrivate( 'getRoleList' )
    def getRoleList( self, info=None ):
        """ Return all the roles defined by a provider.
        """
        return self._roles or ()

    #
    #   ZMI methods
    #
    security.declareProtected( ManagePortal, 'manage_editRolesForm' )
    def manage_editRolesForm( self, REQUEST, manage_tabs_message=None ):

        """ Show the 'Roles' management tab.
        """
        roles = []

        for a in self.getRoleList():

            a1 = {}
            a1['id'] = a.getId()    # The Role Id (ex. Assignor)
            a1['description'] = unicode(a.Description(), 'utf8', 'repr')    # The Role Description (ex. a person in charge of assigning orders)
            a1['name'] = unicode(a.Title(), 'utf8', 'repr')  # The name of this role definition (ex. Assignor at company X)
            a1['category'] = a.getCategory() or [] # Category definition
            a1['base_category'] = a.getBaseCategory() # Base Category Definition
            a1['base_category_script'] = a.getBaseCategoryScript() # Base Category Script Id
            a1['condition'] = a.getCondition()
            roles.append(a1)

        return self._roles_form( self
                                 , REQUEST
                                 , roles=roles
                                 , management_view='Roles'
                                 , manage_tabs_message=manage_tabs_message
                                 )

    security.declareProtected( ManagePortal, 'addRole' )
    def addRole( self
                 , id
                 , description
                 , name
                 , condition
                 , category
                 , base_category_script
                 # XXX Default value is a tuple, but a string is required
                 , base_category=()
                 , REQUEST=None
                 ):
        """ Add an role to our list.
        """
        if not name:
            raise ValueError('A name is required.')

        c_expr = condition and Expression(text=str(condition)) or ''

        new_roles = self._cloneRoles()

        new_role = RoleInformation(     id=str(id)
                                      , description=description
                                      , title=str(name)
                                      , condition=c_expr
                                      , category=category.split('\n')
                                      , base_category=base_category.split()
                                      , base_category_script=base_category_script
                                      )

        new_roles.append( new_role )
        self._roles = tuple( new_roles )

        if REQUEST is not None:
            return self.manage_editRolesForm(
                REQUEST, manage_tabs_message='Added.')

    security.declareProtected( ManagePortal, 'changeRoles' )
    def changeRoles( self, properties=None, REQUEST=None ):

        """ Update our list of roles.
        """
        if properties is None:
            properties = REQUEST

        roles = []

        for index in range( len( self._roles ) ):
            roles.append( self._extractRole( properties, index ) )

        self._roles = tuple( roles )

        if REQUEST is not None:
            return self.manage_editRolesForm(REQUEST, manage_tabs_message=
                                               'Roles changed.')

    security.declareProtected( ManagePortal, 'deleteRoles' )
    def deleteRoles( self, selections=(), REQUEST=None ):

        """ Delete roles indicated by indexes in 'selections'.
        """
        sels = list( map( int, selections ) )  # Convert to a list of integers.

        old_roles = self._cloneRoles()
        new_roles = []

        for index in range( len( old_roles ) ):
            if index not in sels:
                new_roles.append( old_roles[ index ] )

        self._roles = tuple( new_roles )

        if REQUEST is not None:
            return self.manage_editRolesForm(
                REQUEST, manage_tabs_message=(
                'Deleted %d role(s).' % len(sels)))

    security.declareProtected( ManagePortal, 'moveUpRoles' )
    def moveUpRoles( self, selections=(), REQUEST=None ):

        """ Move the specified roles up one slot in our list.
        """
        sels = list( map( int, selections ) )  # Convert to a list of integers.
        sels.sort()

        new_roles = self._cloneRoles()

        for idx in sels:
            idx2 = idx - 1
            if idx2 < 0:
                # Wrap to the bottom.
                idx2 = len(new_roles) - 1
            # Swap.
            a = new_roles[idx2]
            new_roles[idx2] = new_roles[idx]
            new_roles[idx] = a

        self._roles = tuple( new_roles )

        if REQUEST is not None:
            return self.manage_editRolesForm(
                REQUEST, manage_tabs_message=(
                'Moved up %d role(s).' % len(sels)))

    security.declareProtected( ManagePortal, 'moveDownRoles' )
    def moveDownRoles( self, selections=(), REQUEST=None ):

        """ Move the specified roles down one slot in our list.
        """
        sels = list( map( int, selections ) )  # Convert to a list of integers.
        sels.sort()
        sels.reverse()

        new_roles = self._cloneRoles()

        for idx in sels:
            idx2 = idx + 1
            if idx2 >= len(new_roles):
                # Wrap to the top.
                idx2 = 0
            # Swap.
            a = new_roles[idx2]
            new_roles[idx2] = new_roles[idx]
            new_roles[idx] = a

        self._roles = tuple( new_roles )

        if REQUEST is not None:
            return self.manage_editRolesForm(
                REQUEST, manage_tabs_message=(
                'Moved down %d role(s).' % len(sels)))

    #
    #   Helper methods
    #
    security.declarePrivate( '_cloneRoles' )
    def _cloneRoles( self ):

        """ Return a list of roles, cloned from our current list.
        """
        return map( lambda x: x.clone(), list( self._roles ) )

    security.declarePrivate( '_extractRole' )
    def _extractRole( self, properties, index ):

        """ Extract an RoleInformation from the funky form properties.
        """
        id             = str( properties.get( 'id_%d'          % index, '' ) )
        description    = str( properties.get( 'description_%d' % index, '' ) )
        name           = str( properties.get( 'name_%d'        % index, '' ) )
        condition      = str( properties.get( 'condition_%d'   % index, '' ) )
        category       = properties.get( 'category_%d'         % index, '' ).split('\n')
        base_category  = properties.get( 'base_category_%d'    % index, ''  ).split()
        base_category_script = str( properties.get( 'base_category_script_%d' % index, '' ) )

        if not name:
            raise ValueError('A name is required.')

        if condition is not '':
            condition = Expression( text=condition )

        return RoleInformation( id=id
                                , title=name
                                , description=description
                                , condition=condition
                                , category=category
                                , base_category=base_category
                                , base_category_script=base_category_script
                                )

    security.declareProtected( ManagePortal, 'updateRoleMapping' )
    def updateRoleMapping( self, REQUEST=None, manage_tabs_message=None ):
      """Update the local roles in existing objects.
      """
      portal_catalog = self.portal_catalog

      update_role_tag = "%s.%s" % (self.__class__.__name__, "updateRoleMapping")

      object_list = portal_catalog(portal_type = self.id, limit=None)
      # We need to use activities in order to make sure it will
      # work for an important number of objects
      object_list_len = len(object_list)
      portal_activities = self.portal_activities
      object_path_list = [x.path for x in object_list]
      for i in xrange(0, object_list_len, 100):
        current_path_list = object_path_list[i:i+100]
        portal_activities.activate(activity='SQLQueue',
                                   priority=3,
                                   tag=update_role_tag)\
              .callMethodOnObjectList(current_path_list,
                                      'updateLocalRolesOnSecurityGroups',
                                      reindex=False)
        portal_activities.activate(activity='SQLQueue',
                                   priority=3,
                                   after_tag=update_role_tag)\
              .callMethodOnObjectList(current_path_list,
                                      'reindexObjectSecurity')

      if REQUEST is not None:
        return self.manage_editRolesForm(REQUEST,
                 manage_tabs_message='%d objects updated' % (object_list_len,))

InitializeClass(RoleProviderBase)
