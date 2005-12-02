##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

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
