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

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod
from Products.CMFCore.DirectoryView import expandpath
from Products.ZSQLMethods.SQL import SQL

class PatchedFSZSQLMethod(FSZSQLMethod):

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'r')    # not 'rb', as this is a text file!
        try:
            data = file.read()
        finally: file.close()

        RESPONSE = {}
        RESPONSE['BODY'] = data

        self.PUT(RESPONSE,None)


    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        # I guess it's bad to 'reach inside' ourselves like this,
        # but Z SQL Methods don't have accessor methdods ;-)
        s = SQL(self.id,
                self.title,
                self.connection_id,
                self.arguments_src,
                self.src)
        s.manage_advanced(self.max_rows_,
                          self.max_cache_,
                          self.cache_time_,
                          self.class_name_,
                          self.class_file_)
        return s

FSZSQLMethod._readFile = PatchedFSZSQLMethod._readFile
FSZSQLMethod._createZODBClone = PatchedFSZSQLMethod._createZODBClone

from Products.CMFCore import ActionInformation
from AccessControl import ClassSecurityInfo
from Products.CMFCore.Expression import Expression
from types import StringType

ActionInformation.oldActionInformation = ActionInformation.ActionInformation

class PatchedActionInformation(ActionInformation.oldActionInformation):

    security = ClassSecurityInfo()

    def __init__( self
                , id
                , title=''
                , description=''
                , category='object'
                , condition=''
                , permissions=()
                , priority=10
                , visible=1
                , action=''
                , icon=''
                , optional=0
                ):
        """ Set up an instance.
        """
        if condition and type( condition ) == type( '' ):
            condition = Expression( condition )

        if action and type( action ) == type( '' ):
            action = Expression( action )

        if icon and type( icon ) == type( '' ):
            icon = Expression( icon )

        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.condition = condition
        self.permissions = permissions
        self.priority = priority
        self.visible = visible
        self.setActionExpression(action)
        self.setIconExpression(icon)
	self.optional = optional


    def getAction( self, ec ):

        """ Compute the action using context, 'ec'; return a mapping of
            info about the action.
        """
        info = {}
        info['id'] = self.id
        info['name'] = self.Title()
        expr = self.getActionExpression()
        __traceback_info__ = (info['id'], info['name'], expr)
        action_obj = self._getActionObject()
        info['url'] = action_obj and action_obj( ec ) or ''
        expr = self.getIconExpression()
        icon_obj = self._getIconObject()
        info['icon'] = icon_obj and icon_obj( ec ) or ''
        info['permissions'] = self.getPermissions()
        info['category'] = self.getCategory()
        info['visible'] = self.getVisibility()
        info['optional'] = self.getOption()
        return info


    security.declarePrivate( '_getIconObject' )
    def _getIconObject( self ):

        """ Find the icon object
        """
        return getattr( self, 'icon', None )


    security.declarePublic( 'getIconExpression' )
    def getIconExpression( self ):

        """ Return the text of the TALES expression for our icon.
        """
        icon = self._getIconObject()
        expr = icon and icon.text or ''
        if expr and type( expr ) is StringType:
            if not expr.startswith('python:') and not expr.startswith('string:'):
                expr = 'string:${object_url}/%s' % expr
                self.icon = Expression( expr )
        return expr


    security.declarePrivate( 'setIconExpression' )
    def setIconExpression(self, icon):
        if icon and type( icon ) is StringType:
            if not icon.startswith('python:')  and not icon.startswith('string:'):
                icon = 'string:${object_url}/%s' % icon
                icon = Expression( icon )
        self.icon = icon


    security.declarePublic( 'getOption' )
    def getOption( self ):

        """ Return whether the action should be optional in the Business Template.
        """
        return getattr( self, 'optional', 0 )

    def clone( self ):

        """ Return a newly-created AI just like us.
        """
        return self.__class__( id=self.id
                             , title=self.title
                             , description=self.description
                             , category =self.category
                             , condition=self.getCondition()
                             , permissions=self.permissions
                             , priority =self.priority
                             , visible=self.visible
                             , action=self.getActionExpression()
                             , icon=self.getIconExpression()
                             , optional=self.getOption()
                             )

ActionInformation.ActionInformation = PatchedActionInformation

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionInformation import ActionInformation

class PatchedActionProviderBase(ActionProviderBase):

    def manage_editActionsForm( self, REQUEST, manage_tabs_message=None ):

        """ Show the 'Actions' management tab.
        """
        actions = []

        for a in self.listActions():

            a1 = {}
            a1['id'] = a.getId()
            a1['name'] = a.Title()
            p = a.getPermissions()
            if p:
                a1['permission'] = p[0]
            else:
                a1['permission'] = ''
            a1['category'] = a.getCategory() or 'object'
            a1['visible'] = a.getVisibility()
            a1['action'] = a.getActionExpression()
            a1['icon'] = a.getIconExpression()
            a1['condition'] = a.getCondition()
            a1['optional'] = a.getOption()
            actions.append(a1)

        # possible_permissions is in AccessControl.Role.RoleManager.
        pp = self.possible_permissions()
        return self._actions_form( self
                                 , REQUEST
                                 , actions=actions
                                 , possible_permissions=pp
                                 , management_view='Actions'
                                 , manage_tabs_message=manage_tabs_message
                                 )


    def addAction( self
                 , id
                 , name
                 , action
                 , condition
                 , permission
                 , category
                 , icon=None
                 , visible=1
                 , optional=0
                 , REQUEST=None
                 ):
        """ Add an action to our list.
        """
        if not name:
            raise ValueError('A name is required.')

        a_expr = action and Expression(text=str(action)) or ''
        i_expr = icon and Expression(text=str(icon)) or ''
        c_expr = condition and Expression(text=str(condition)) or ''

        if type( permission ) != type( () ):
            permission = permission and (str(permission),) or ()

        new_actions = self._cloneActions()

        new_action = ActionInformation( id=str(id)
                                      , title=str(name)
                                      , action=a_expr
                                      , icon=i_expr
                                      , condition=c_expr
                                      , permissions=permission
                                      , category=str(category)
                                      , visible=int(visible)
                                      , optional=int(optional)
                                      )

        new_actions.append( new_action )
        self._actions = tuple( new_actions )

        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message='Added.')


    def _extractAction( self, properties, index ):

        """ Extract an ActionInformation from the funky form properties.
        """
        id          = str( properties.get( 'id_%d'          % index, '' ) )
        name        = str( properties.get( 'name_%d'        % index, '' ) )
        action      = str( properties.get( 'action_%d'      % index, '' ) )
        icon        = str( properties.get( 'icon_%d'        % index, '' ) )
        condition   = str( properties.get( 'condition_%d'   % index, '' ) )
        category    = str( properties.get( 'category_%d'    % index, '' ))
        visible     =      properties.get( 'visible_%d'     % index, 0  )
        optional    =      properties.get( 'optional_%d'    % index, 0  )
        permissions =      properties.get( 'permission_%d'  % index, () )

        if not name:
            raise ValueError('A name is required.')

        if action is not '':
            action = Expression( text=action )

        if icon is not '':
            icon = Expression( text=icon )

        if condition is not '':
            condition = Expression( text=condition )

        if category == '':
            category = 'object'

        if type( visible ) is not type( 0 ):
            try:
                visible = int( visible )
            except:
                visible = 0

        if type( optional ) is not type( 0 ):
            try:
                optional = int( optional )
            except:
                optional = 0

        if type( permissions ) is type( '' ):
            permissions = ( permissions, )

        return ActionInformation( id=id
                                , title=name
                                , action=action
                                , icon=icon
                                , condition=condition
                                , permissions=permissions
                                , category=category
                                , visible=visible
                                , optional=optional
                                )

ActionProviderBase.manage_editActionsForm = PatchedActionProviderBase.manage_editActionsForm
ActionProviderBase.addAction = PatchedActionProviderBase.addAction
ActionProviderBase._extractAction = PatchedActionProviderBase._extractAction

