##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002-2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent

import Products.CMFCore.TypesTool
from Products.CMFCore.TypesTool import TypeInformation, ScriptableTypeInformation, FactoryTypeInformation, TypesTool
from Products.CMFCore.interfaces.portal_types import ContentTypeInformation as ITypeInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.Expression import createExprContext

from Products.ERP5Type import _dtmldir
from Products.ERP5Type import Permissions as ERP5Permissions

from RoleProviderBase import RoleProviderBase
from RoleInformation import ori

from zLOG import LOG

import re
action_basename_re = re.compile("\/([^\/\?]+)(\?.+)?$")

ERP5TYPE_ROLE_INIT_SCRIPT = 'ERP5Type_initLocalRoleMapping'

class ERP5TypeInformation( FactoryTypeInformation, RoleProviderBase ):
    """
    ERP5 Types are based on FactoryTypeInformation

    The most important feature of ERP5Types is programmable acquisition which
    allows defining attributes which are acquired through categories.

    Another feature is to define the way attributes are stored (localy,
    database, etc.). This allows combining multiple attribute sources
    in a single object. This feature will be in reality implemented
    through PropertySheet classes (TALES expressions)
    """

    __implements__ = ITypeInformation

    meta_type = 'ERP5 Type Information'
    security = ClassSecurityInfo()

    manage_options = ( SimpleItemWithProperties.manage_options[:1]
                     + ActionProviderBase.manage_options
                     + RoleProviderBase.manage_options
                     + SimpleItemWithProperties.manage_options[1:]
                     )

    _properties = (TypeInformation._basic_properties + (
        {'id':'factory', 'type': 'string', 'mode':'w',
         'label':'Product factory method'},
        {'id':'init_script', 'type': 'string', 'mode':'w',
         'label':'Init Script'},
        {'id':'filter_content_types', 'type': 'boolean', 'mode':'w',
         'label':'Filter content types?'},
        {'id':'allowed_content_types'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Allowed content types'
         , 'select_variable':'listContentTypes'
         },
        {'id':'hidden_content_type_list'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Hidden content types'
         , 'select_variable':'listContentTypes'
         },
        {'id':'property_sheet_list'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Property Sheets'
         , 'select_variable':'getPropertySheetList'
         },
        {'id':'base_category_list'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Base Categories'
         , 'select_variable':'getBaseCategoryList'
         },
        {'id':'filter_actions', 'type': 'boolean', 'mode':'w',
         'label':'Filter actions?'},
        {'id':'allowed_action_list'
         , 'type': 'lines'
         , 'mode':'w'
         , 'label':'Allowed actions'
         },
        ))

    property_sheet_list = ()
    base_category_list = ()
    init_script = ''
    product = 'ERP5Type'
    immediate_view = 'view'
    hidden_content_type_list = ()
    filter_actions = 0
    allowed_action_list = []

    #
    #   Acquisition editing interface
    #

    _actions_form = DTMLFile( 'editToolsActions', _dtmldir )

    security.declarePublic('hideFromAddMenu')
    def hidenFromAddMenu(self):
      """
      Return only true or false if we should
      hide from add menu
      """
      return self.hiden_from_add_menu


    #
    #   Agent methods
    #
    security.declarePublic('constructInstance')
    def constructInstance( self, container, id, *args, **kw ):
        """
        Build a "bare" instance of the appropriate type in
        'container', using 'id' as its id.  Return the object.
        """
        ob = FactoryTypeInformation.constructInstance(self, container, id, *args, **kw)

        # Try to find the local role init script
        init_role_script = getattr(ob, ERP5TYPE_ROLE_INIT_SCRIPT, None)
        if init_role_script is not None:
          # Retrieve applicable roles
          role_mapping = self.getFilteredRoleListFor(object = self) # kw provided in order to take any appropriate action
          # Call the local role init script
          init_role_script(role_mapping = role_mapping, **kw)

        if self.init_script:
          # Acquire the init script in the context of this object
          init_script = getattr(ob, self.init_script)
          init_script(*args, **kw)

        return ob

    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'getPropertySheetList')
    def getPropertySheetList( self ):
        """
            Return list of content types.
        """
        from Products.ERP5Type import PropertySheet
        result = PropertySheet.__dict__.keys()
        result = filter(lambda k: not k.startswith('__'),  result)
        result.sort()
        return result

    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'getHiddenContentTypeList')
    def getHiddenContentTypeList( self ):
        """
            Return list of content types.
        """
        return self.hidden_content_type_list

    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'isActionAllowed')
    def isActionAllowed( self, action=None ):
        """
            Return list of allowed actions.

            You can define a 'allowed_action_list' property (as lines) on the portal_types object
            to define actions that will be available for all portal types.
        """
        if not self.filter_actions :
          return 1 # everything is allowed

        global_allowed_action_list = list(self.portal_types.getProperty('allowed_action_list', []))
        action_list = list(self.allowed_action_list) + global_allowed_action_list
        for ob_action in self._actions :
          action_basename = action_basename_re.search(ob_action.action.text).group(1)
          if len(action_basename) :
            action_list.append(action_basename_re.search(ob_action.action.text).group(1))

        LOG('isActionAllowed for %s :' % self.title_or_id(), 0, 'looking for %s in %s : %s' % (action, action_list, action in action_list))
        if action in action_list :
          return 1
        return 0

    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'getBaseCategoryList')
    def getBaseCategoryList( self ):
        result = self.portal_categories.getBaseCategoryList()
        result.sort()
        return result

    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'getConstraintList')
    def getConstraintList( self ):
        from Products.ERP5Type import Constraint
        result = Constraint.__dict__.keys()
        result = filter(lambda k: k != 'Constraint' and not k.startswith('__'),  result)
        result.sort()
        return result

    security.declarePublic('getFilteredRoleListFor')
    def getFilteredRoleListFor(self, object=None, **kw):
        """
        Return a mapping containing of all roles applicable to the
        object against user.
        """
        portal = aq_parent(aq_inner(self))
        if object is None or not hasattr(object, 'aq_base'):
            folder = portal
        else:
            folder = object
            # Search up the containment hierarchy until we find an
            # object that claims it's a folder.
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    folder = aq_parent(aq_inner(folder))

        ec = createExprContext(folder, portal, object)
        roles = []
        append = roles.append
        info = ori(self, folder, object)

        # Include actions from self
        self._filterRoleList(append,self,info,ec)

        # Reorganize the actions by role,
        # filtering out disallowed actions.
        filtered_roles={
                       }
        for role in roles:
            id = role['id']
            if not filtered_roles.has_key(id):
                filtered_roles[id] = []
            filtered_roles[id].append(role)

        return filtered_roles

    #
    #   Helper methods
    #
    def _filterRoleList(self,append,object,info,ec):
        r = object.getRoleList(info)
        if r and type(r[0]) is not type({}):
            for ri in r:
                if ri.testCondition(ec):
                    append(ri.getRole(ec))
        else:
            for i in r:
                append(i)

    def manage_editProperties(self, REQUEST):
      """
        Method overload

        Reset _aq_dynamic if property_sheet definition has changed)

        XXX This is only good in single thread mode.
            In ZEO environment, we should call portal_activities
            in order to implement a broadcast update
            on production hosts
      """
      previous_property_sheet_list = self.property_sheet_list
      base_category_list = self.base_category_list
      result = FactoryTypeInformation.manage_editProperties(self, REQUEST)
      if previous_property_sheet_list != self.property_sheet_list or \
                   base_category_list != self.base_category_list:
        from Products.ERP5Type.Base import _aq_reset
        _aq_reset() # XXX We should also call it whenever we change workflow defitino
      return result

    security.declareProtected( ERP5Permissions.ManagePortal, 'manage_editLocalRolesForm' )
    def manage_editLocalRolesForm( self, REQUEST, manage_tabs_message=None ):

        """ Show the 'Local Roles' management tab.
        """
        role_list = []

        return self._roles_form( self
                                 , REQUEST
                                 , roles=role_list
                                 , possible_permissions=()
                                 , management_view='Roles'
                                 , manage_tabs_message=manage_tabs_message
                                 )


InitializeClass( ERP5TypeInformation )

typeClasses = [
    {'class':FactoryTypeInformation,
     'name':FactoryTypeInformation.meta_type,
     'action':'manage_addFactoryTIForm',
     'permission':'Manage portal'},
    {'class':ScriptableTypeInformation,
     'name':ScriptableTypeInformation.meta_type,
     'action':'manage_addScriptableTIForm',
     'permission':'Manage portal'},
    {'class':ERP5TypeInformation,
     'name':ERP5TypeInformation.meta_type,
     'action':'manage_addERP5TIForm',
     'permission':'Manage portal'},
    ]

class ERP5TypesTool(TypesTool):
    """
      Only used to patch standard TypesTool
    """
    meta_type = 'ERP5 Type Information'

    security = ClassSecurityInfo()

    security.declareProtected(ERP5Permissions.ManagePortal, 'manage_addERP5TIForm')
    def manage_addERP5TIForm(self, REQUEST):
        ' '
        return self._addTIForm(
            self, REQUEST,
            add_meta_type=ERP5TypeInformation.meta_type,
            types=self.listDefaultTypeInformation())


# Dynamic patch
Products.CMFCore.TypesTool.typeClasses = typeClasses
Products.CMFCore.TypesTool.TypesTool.manage_addERP5TIForm = ERP5TypesTool.manage_addERP5TIForm

