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

from Globals import DTMLFile
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import _dtmldir

def ActionProviderBase_manage_editActionsForm( self, REQUEST, manage_tabs_message=None ):

    """ Show the 'Actions' management tab.
    """
    actions = []

    for a in self.listActions():

        a1 = {}
        a1['id'] = a.getId()
        a1['title'] = a1['name'] = a.Title()
        p = a.getPermissions()
        a1['permissions'] = p
        if p:
            a1['permission'] = p[0]
        else:
            a1['permission'] = ''
        a1['category'] = a.getCategory() or 'object'
        a1['visible'] = a.getVisibility()
        a1['action'] = a.getActionExpression()
        a1['condition'] = a.getCondition()
        if hasattr(a, 'getPriority') :
          a1['priority'] = a.getPriority()
        if hasattr(a, 'getIconExpression') :
          a1['icon'] = a.getIconExpression()
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


def ActionProviderBase_addAction( self
              , id
              , name
              , action
              , condition
              , permission
              , category
              , icon=None
              , visible=1
              , priority=1.0
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
                                  , priority=float(priority)
                                  )

    new_actions.append( new_action )
    self._actions = tuple( new_actions )

    if REQUEST is not None:
        return self.manage_editActionsForm(
            REQUEST, manage_tabs_message='Added.')


def ActionProviderBase_extractAction( self, properties, index ):

    """ Extract an ActionInformation from the funky form properties.
    """
    id          = str( properties.get( 'id_%d'          % index, '' ) )
    name        = str( properties.get( 'name_%d'        % index, '' ) )
    action      = str( properties.get( 'action_%d'      % index, '' ) )
    icon        = str( properties.get( 'icon_%d'        % index, '' ) )
    condition   = str( properties.get( 'condition_%d'   % index, '' ) )
    category    = str( properties.get( 'category_%d'    % index, '' ))
    visible     =      properties.get( 'visible_%d'     % index, 0  )
    permissions =      properties.get( 'permission_%d'  % index, () )
    priority    = float( properties.get( 'priority_%d'    % index, 1.0 ))

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
        except TypeError:
            visible = 0

    if type( permissions ) is type( '' ):
        permissions = ( permissions, )

    if type( priority ) is not type(1.0):
        priority = float(priority)

    return ActionInformation( id=id
                            , title=name
                            , action=action
                            , icon=icon
                            , condition=condition
                            , permissions=permissions
                            , category=category
                            , visible=visible
                            , priority=priority
                            )

ActionProviderBase.manage_editActionsForm = ActionProviderBase_manage_editActionsForm
ActionProviderBase.addAction = ActionProviderBase_addAction
ActionProviderBase._extractAction = ActionProviderBase_extractAction
ActionProviderBase._actions_form = DTMLFile( 'editToolsActions', _dtmldir )
