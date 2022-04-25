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
from six import string_types as basestring

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
        if expr and isinstance(expr, basestring):
            if not expr.startswith('python:') and not expr.startswith('string:'):
                expr = 'string:${object_url}/%s' % expr
                self.icon = Expression( expr )
        return expr

    security.declarePrivate( 'setIconExpression' )
    def setIconExpression(self, icon):
        if icon and isinstance(icon, basestring):
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

    ActionInformation_getMapping = ActionInformation.getMapping
    def getMapping(self):
        """ Get a mapping of this object's data.
        """
        mapping = ActionInformation_getMapping(self)
        # missing on CMF 1.5, provided as icon_expression on CMF 2
        mapping['icon'] = icon=self.getIconExpression()
        # missing on both CMF 1.5 and 2
        mapping['priority'] = self.getPriority()
        return mapping

ActionInformation.__init__ = __init__
ActionInformation.getAction = getAction
ActionInformation._getIconObject = _getIconObject
ActionInformation._getIconExpressionObject = _getIconObject
ActionInformation.getIconExpression = getIconExpression
ActionInformation.setIconExpression = setIconExpression
ActionInformation.getDescription = getDescription
ActionInformation.getPriority = getPriority
ActionInformation.clone = clone
ActionInformation.getMapping = getMapping

PatchedActionInformation = ActionInformation

if 1:
  from Products.CMFCore.ActionInformation import ActionInfo

  original_init = ActionInfo.__init__
  def __init__(self, action, ec):
    original_init(self, action, ec)
    if not isinstance(action, dict):
      # ivan
      if self.data.get('icon') is not None:
        def getIcon(ec=ec):
          # On CMF 2.2 the ec parameter is not passed.
          icon_expression_obj = action._getIconObject()
          if icon_expression_obj not in ('',  None):
            return icon_expression_obj(ec)
        self.data['icon'] = getIcon
        self._lazy_keys.append('icon')
      else:
        self.data['icon'] = ''
    # put back 'name' if it's not there. CMF 2.x removes it.
    self.data['name'] = self['title']

  ActionInfo.__init__ = __init__
