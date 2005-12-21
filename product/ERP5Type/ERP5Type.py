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
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base, aq_inner, aq_parent

import Products.CMFCore.TypesTool
from Products.CMFCore.TypesTool import TypeInformation, ScriptableTypeInformation, FactoryTypeInformation, TypesTool
from Products.CMFCore.interfaces.portal_types import ContentTypeInformation as ITypeInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.Expression import createExprContext

from Products.ERP5Type import _dtmldir
from Products.ERP5Type import Permissions as ERP5Permissions

# Security uses ERP5Security by default
try:
  from Products.ERP5Security import ERP5UserManager
except ImportError:
  ERP5UserManager = None

# If ERP5Security is not installed try NuxUserGroups
if ERP5UserManager is None:
  try:
    from Products import NuxUserGroups
  except ImportError:
    NuxUserGroups = None

from RoleProviderBase import RoleProviderBase
from RoleInformation import ori

from zLOG import LOG

ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT = 'ERP5Type_asSecurityGroupId'

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
        {'id':'acquire_local_roles'
         , 'type': 'boolean'
         , 'mode':'w'
         , 'label':'Acquire Local Roles'
         },
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
        {'id':'group_list'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Groups'
         , 'select_variable':'getGroupList'
         },
        ))

    acquire_local_roles = True
    property_sheet_list = ()
    base_category_list = ()
    init_script = ''
    product = 'ERP5Type'
    immediate_view = 'view'
    hidden_content_type_list = ()
    filter_actions = 0
    allowed_action_list = []

    # Groups are used to classify portal types (e.g. resource).
    defined_group_list = (
      'accounting_transaction', 'accounting_movement', 'alarm', 'balance_transaction_line',
      'container', 'container_line', 'delivery', 'delivery_movement',
      'discount', 'invoice', 'invoice_movement', 'item',
      'order', 'order_movement', 'node', 'payment_condition',
      'resource', 'supply', 'transformation', 'variation',
      'sub_variation'
    )
    group_list = ()

    #
    #   Acquisition editing interface
    #

    _actions_form = DTMLFile( 'editToolsActions', _dtmldir )

    security.declarePrivate('_guessMethodAliases')
    def _guessMethodAliases(self):
        """ Override this method to disable Method Aliases in ERP5.
        """
        self.setMethodAliases({})
        return 1

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
    def constructInstance( self, container, id, bypass_init_script=0, 
                                 *args, **kw ):
        """
        Build a "bare" instance of the appropriate type in
        'container', using 'id' as its id.
        Call the init_script for the portal_type, unless the
        keyword arg __bypass_init_script is set to True.
        Returns the object.
        """
        # This is part is copied from CMFCore/TypesTool
        ob = FactoryTypeInformation.constructInstance(
                                             self, container, id, *args, **kw)

        # Only try to assign roles to secutiry groups if some roles are defined
        # This is an optimisation to prevent defining local roles on subobjects
        # which acquire their security definition from their parent
        # The downside of this optimisation is that it is not possible to
        # set a local role definition if the local role list is empty
        if len(self._roles):
            self.assignRoleToSecurityGroup(ob)

        # TODO: bypass_init_script must be passed as an argument
        # to the init_script, and the init_script must always be called;
        # so that user can decide what init should be done when this is 
        # created by DeliveryBuilder.
        if self.init_script and not bypass_init_script:
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

    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'getGroupList')
    def getGroupList( self ):
        return self.defined_group_list

    security.declareProtected(ERP5Permissions.ModifyPortalContent, 'assignRoleToSecurityGroup')
    def assignRoleToSecurityGroup(self, object):
        """
        Assign Local Roles to Groups on object, based on Portal Type Role Definitions
        """
        #FIXME We should check the type of the acl_users folder instead of
        #      checking which product is installed.
        if ERP5UserManager is not None:
          user_name = getSecurityManager().getUser().getId() # We use id for roles in ERP5Security
        elif NuxUserGroups is not None:
          user_name = getSecurityManager().getUser().getUserName()
        else:
          raise RuntimeError, 'Product "NuxUserGroups" was not found on your setup. '\
                'Please install it to benefit from group-based security'

        # Retrieve applicable roles
        role_mapping = self.getFilteredRoleListFor(object=object) # kw provided in order to take any appropriate action
        role_category_list = {}
        for role, definition_list in role_mapping.items():
            if not role_category_list.has_key(role):
                role_category_list[role] = []
            # For each role definition, we look for the base_category_script
            # and try to use it to retrieve the values for the base_category list
            for definition in definition_list:
                # get the list of base_categories that are statically defined
                category_base_list = [x.split('/')[0] for x in definition['category']]
                # get the list of base_categories that are to be fetched through the script
                actual_base_category_list = [x for x in definition['base_category'] if x not in category_base_list]
                # get the aggregated list of base categories, to preserve the order
                category_order_list = []
                category_order_list.extend(definition['base_category'])
                for bc in category_base_list:
                    if bc not in category_order_list:
                        category_order_list.append(bc)

                # get the script and apply it if actual_base_category_list is not empty
                if len(actual_base_category_list) > 0:
                    base_category_script_id = definition['base_category_script']
                    base_category_script = getattr(object, base_category_script_id, None)
                    if base_category_script is not None:
                        # call the script, which should return either a dict or a list of dicts
                        category_result = base_category_script(actual_base_category_list, user_name, object, object.getPortalType())
                        # If we decide in the script that we don't want to update the security for this object,
                        # we can just have it return None instead of a dict or list of dicts
                        if category_result is None:
                            continue
                        if type(category_result) is type({}):
                            category_result = [category_result]
                    else:
                        raise RuntimeError, 'Script %s was not found to fetch values for'\
                                ' base categories : %s' % (base_category_script_id,
                                                      ', '.join(actual_base_category_list))
                else:
                    category_result = [{}]
                # add the result to role_category_list, aggregated with category_order and statically defined categories
                for category_dict in category_result:
                    category_value_dict = {'category_order':category_order_list}
                    category_value_dict.update(category_dict)
                    for c in definition['category']:
                        bc, value = c.split('/', 1)
                        category_value_dict[bc] = value
                    role_category_list[role].append(category_value_dict)

        # Generate security group ids from category_value_dicts
        role_group_id_dict = {}
        group_id_generator = getattr(object, ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT, None)
        if group_id_generator is None:
            raise RuntimeError, '%s script was not found' % ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT
        for role, value_list in role_category_list.items():
            if not role_group_id_dict.has_key(role):
                role_group_id_dict[role] = []
            role_group_dict = {}
            for category_dict in value_list:
                group_id = group_id_generator(**category_dict)
                role_group_dict[group_id] = 1
            role_group_id_dict[role].extend(role_group_dict.keys())

        # Switch index from role to group id
        group_id_role_dict = {}
        for role, group_list in role_group_id_dict.items():
            for group_id in group_list:
                if not group_id_role_dict.has_key(group_id):
                    group_id_role_dict[group_id] = []
                group_id_role_dict[group_id].append(role)

        # Update role assignments to groups
        if ERP5UserManager is not None: # Default implementation
          # Clean old group roles
          old_group_list = object.get_local_roles()
          object.manage_delLocalRoles([x[0] for x in old_group_list])
          # Save the owner
          for group, role_list in old_group_list:
            if 'Owner' in role_list:
              if group not in group_id_role_dict.keys():
                group_id_role_dict[group] = ('Owner',)
              else:
                group_id_role_dict[group].append('Owner')
          # Assign new roles
          for group, role_list in group_id_role_dict.items():
              object.manage_addLocalRoles(group, role_list)
        else: # NuxUserGroups implementation
          # Clean old group roles
          old_group_list = object.get_local_group_roles()
          object.manage_delLocalGroupRoles([x[0] for x in old_group_list])
          # Assign new roles
          for group, role_list in group_id_role_dict.items():
              object.manage_addLocalGroupRoles(group, role_list)

    security.declarePublic('getFilteredRoleListFor')
    def getFilteredRoleListFor(self, object=None, **kw):
        """
        Return a mapping containing of all roles applicable to the
        object against user.
        """
        portal = self.portal_url.getPortalObject()
        if object is None:
          folder = portal
        else:
          folder = aq_parent(object)
          # Search up the containment hierarchy until we find an
          # object that claims it's a folder.
          while folder is not None:
            if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
              # found it.
              break
            else:
              folder = aq_parent(folder)

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
        _aq_reset() # XXX We should also call it whenever we change workflow defition
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

