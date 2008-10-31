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

from Products.CMFCore.ActionInformation import ActionInformation
from AccessControl import ClassSecurityInfo
from Products.CMFCore.Expression import Expression
from types import StringType

if 1:

    security = ClassSecurityInfo()

    def __init__( self
                , id
                , title=''
                , description=''
                , category='object'
                , condition=''
                , permissions=()
                , priority=1.0
                , visible=1
                , action=''
                , icon=''
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

    def getAction( self, ec ):

        """ Compute the action using context, 'ec'; return a mapping of
            info about the action.
        """
        info = {}
        info['id'] = self.id
        info['name'] = self.Title()
        info['description'] = self.getDescription()
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
        info['priority'] = self.getPriority()
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

    def getPriority( self ):
        """
        Return the priority of the action
        """
        return getattr(self, 'priority', 1.0)

    def getDescription( self ):
        """
        Return the priority of the action
        """
        return getattr(self, 'description', '')

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
                             )

    def getMapping(self):
        """ Get a mapping of this object's data.
        """
        return { 'id': self.id,
                 'title': self.title or self.id,
                 'description': self.description,
                 'category': self.category or 'object',
                 'condition': getattr(self, 'condition', None)
                              and self.condition.text or '',
                 'permissions': self.permissions,
                 'visible': bool(self.visible),
                 'action': self.getActionExpression(),
                 'icon': self.getIconExpression(),
                 'priority': self.getPriority() }


ActionInformation.__init__ = __init__
ActionInformation.getAction = getAction
ActionInformation._getIconObject = _getIconObject
ActionInformation.getIconExpression = getIconExpression
ActionInformation.setIconExpression = setIconExpression
ActionInformation.getDescription = getDescription
ActionInformation.getPriority = getPriority
ActionInformation.clone = clone
ActionInformation.getMapping = getMapping

PatchedActionInformation = ActionInformation

try:
  from Products.CMFCore.ActionInformation import ActionInfo

  original_init = ActionInfo.__init__
  def __init__(self, action, ec):
    original_init(self, action, ec)
    if not isinstance(action, dict):
      if self.data['icon']:
        self.data['icon'] = self._getIcon
        self._lazy_keys.append('icon')
      else:
        self.data['icon'] = ''

  def _getIcon(self):
    return self._action._getIconObject()(self._ec)

  ActionInfo.__init__ = __init__
  ActionInfo._getIcon = _getIcon
except ImportError:
  pass
