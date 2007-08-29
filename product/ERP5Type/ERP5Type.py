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

import Products
import Products.CMFCore.TypesTool
from Products.CMFCore.TypesTool import TypeInformation
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.interfaces.portal_types import ContentTypeInformation\
                                                as ITypeInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type import PropertySheet
from Products.ERP5Type import _dtmldir
from Products.ERP5Type import Permissions

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

from TranslationProviderBase import TranslationProviderBase

from zLOG import LOG

ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT = 'ERP5Type_asSecurityGroupId'

class ERP5TypeInformation( FactoryTypeInformation,
                           RoleProviderBase,
                           TranslationProviderBase ):
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
                     + TranslationProviderBase.manage_options
                     + SimpleItemWithProperties.manage_options[1:]
                     )

    _properties = (TypeInformation._basic_properties + (
        {'id':'factory', 'type': 'string', 'mode':'w',
         'label':'Product factory method'},
        {'id':'permission', 'type': 'string', 'mode':'w',
         'label':'Add permission'},
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
    permission = ''

    # Groups are used to classify portal types (e.g. resource).
    # IMPLEMENTATION NOTE
    # The current implementation is practical but not modular at all
    # Providing extensible document groups will be desirable at some point
    # Implementation could consist for example in allowing to define
    # the list of groups at the level of ERP5Site either
    # with a default value or with a user specified value. Accessors
    # to portal type groups should then be generated dynamically through
    # _aq_dynamic. This would provide limitless group definition.
    # The main issue in providing too much flexibility at this level
    # is to reduce standardisation. New groups should therefore be handled
    # with great care.
    defined_group_list = (
      # Framework
      'alarm',
      # ERP5 UBM (5 Classes)
      'resource', 'node', 'item', 
      'delivery', 'delivery_movement',
      'order', 'order_movement',
      'container', 'container_line',
      # Trade
      'discount',  'payment_condition', 'payment_node',
      'supply', 'supply_path',
      # PDM
      'transformation', 'variation', 'sub_variation',
      # Accounting
      'accounting_transaction', 'accounting_movement',
      'invoice', 'invoice_movement', 'balance_transaction_line',
      # CRM
      'event', 'ticket',
      # DMS
      'document', 'web_document', 'file_document',
      'recent_document', 'my_document', 'template_document',
      'crawler_index',
      # MRP
      'divergence_tester', 'calendar_period',
      # Project
      'project',
      # Module
      'module',
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

    #
    #   Agent methods
    #
    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed( self, container ):
        """
        Does the current user have the permission required in
        order to construct an instance?
        """
        permission = self.permission
        if permission and not _checkPermission( permission, container ):
            return 0
        return FactoryTypeInformation.isConstructionAllowed(self, container)

    def _getFactoryMethod(self, container, check_security=1):
        if not self.product or not self.factory:
            raise ValueError, ('Product factory for %s was undefined' %
                               self.getId())
        p = container.manage_addProduct[self.product]
        if hasattr(container, 'isTempObject') and container.isTempObject():
          factory_name = self.factory.replace('add', 'newTemp') # We suppose here
                         # that methods are names addClass or newTempClass
                         # Prefix should be moved to a central place.
          m = getattr(p, factory_name, None)
        else:
          m = getattr(p, self.factory, None)
        if m is None:
            raise ValueError, ('Product factory for %s was invalid' %
                               self.getId())
        if not check_security:
            return m
        if getSecurityManager().validate(p, p, self.factory, m):
            return m
        raise AccessControl_Unauthorized( 'Cannot create %s' % self.getId() )
    
    security.declarePublic('constructInstance')
    def constructInstance( self, container, id,
                           created_by_builder=0, *args, **kw ):
        """
        Build a "bare" instance of the appropriate type in
        'container', using 'id' as its id.
        Call the init_script for the portal_type.
        Returns the object.
        """
        # This is part is copied from CMFCore/TypesTool/constructInstance
        # In case of temp object, we don't want to check security
        if not (hasattr(container, 'isTempObject') and container.isTempObject())\
               and not self.isConstructionAllowed(container):
            raise AccessControl_Unauthorized('Cannot create %s' % self.getId())

        # Then keep on the construction process
        ob = self._constructInstance(container, id, *args, **kw)
        ob = self._finishConstruction(ob)

        # Only try to assign roles to security groups if some roles are defined
        # This is an optimisation to prevent defining local roles on subobjects
        # which acquire their security definition from their parent
        # The downside of this optimisation is that it is not possible to
        # set a local role definition if the local role list is empty
        if len(self._roles):
            self.updateLocalRolesOnSecurityGroups(ob)

        if self.init_script :
            # Acquire the init script in the context of this object
            init_script = getattr(ob, self.init_script)
            kw['created_by_builder'] = created_by_builder
            init_script(*args, **kw)

        return ob

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getPropertySheetList')
    def getPropertySheetList( self ):
        """
            Return list of content types.
            XXX I (seb) think the name is bad
                (jp) yes, the name is bad, it should be getAvailablePropertySheetList
        """
        result = Products.ERP5Type.PropertySheet.__dict__.keys()
        result = filter(lambda k: not k.startswith('__'),  result)
        result.sort()
        return result

    security.declareProtected(Permissions.ManagePortal,
                              'setPropertySheetList')
    def setPropertySheetList( self, property_sheet_list):
        """
          Set the list of property_sheet for this portal type
        """
        self.property_sheet_list = property_sheet_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getHiddenContentTypeList')
    def getHiddenContentTypeList( self ):
        """
            Return list of content types.
        """
        return self.hidden_content_type_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getBaseCategoryList')
    def getBaseCategoryList( self ):
        result = self.portal_categories.getBaseCategoryList()
        result.sort()
        return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getConstraintList')
    def getConstraintList( self ):
        result = Products.ERP5Type.Constraint.__dict__.keys()
        result = filter(lambda k: k != 'Constraint' and not k.startswith('__'),
                        result)
        result.sort()
        return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getGroupList')
    def getGroupList( self ):
        return self.defined_group_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstanceBaseCategoryList')
    def getInstanceBaseCategoryList(self):
      """ Return all base categories of the portal type """
      current_list = []
      ptype_object = self
      # get the klass of the object based on the constructor document
      m = Products.ERP5Type._m
      constructor = self.factory
      klass = None
      for method, doc in m.items():
        if method == constructor:
          klass = doc.klass
          break

      # get categories from portal type
      cat_list = ptype_object.base_category_list
      current_list += cat_list
      # get categories from property sheet
      ps_list = map(lambda p: getattr(PropertySheet, p, None),
                    ptype_object.property_sheet_list)
      ps_list = filter(lambda p: p is not None, ps_list)
      # from the property sheets defined on the class
      if klass is not None:
        from Products.ERP5Type.Base import getClassPropertyList
        ps_list = tuple(ps_list) + getClassPropertyList(klass)
      for base in ps_list:
        ps_property = getattr(base, '_categories', None)
        if type(ps_property) in (type(()), type([])):
          cat_dict_list = []
          for category in ps_property:
            if category not in current_list:
              current_list.append(category)
      return current_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstancePropertyAndBaseCategoryList')
    def getInstancePropertyAndBaseCategoryList(self):
      """Return all the properties and base categories of the portal type. """
      ptype_object = self
      # get the klass of the object based on the constructor document
      m = Products.ERP5Type._m
      constructor = self.factory
      klass = None
      for method, doc in m.items():
        if method == constructor:
          klass = doc.klass
          break
      # get the property sheet list for the portal type
      # from the list of property sheet defined on the portal type
      ps_list = map(lambda p: getattr(PropertySheet, p, None),
                  ptype_object.property_sheet_list)
      cat_list = ptype_object.base_category_list
      ps_list = filter(lambda p: p is not None, ps_list)
      # from the property sheets defined on the class
      if klass is not None:
        from Products.ERP5Type.Base import getClassPropertyList
        ps_list = tuple(ps_list) + getClassPropertyList(klass)
      # get all properties from the property sheet list
      current_list = []
      current_list += cat_list
      for base in ps_list:
        ps_property = getattr(base, '_properties', None)
        if type(ps_property) in (type(()), type([])):
          for prop in ps_property:
            if prop['type'] != 'content':
              if prop['id'] not in current_list:
                current_list.append(prop['id'])
            else:
              suffix_list = prop['acquired_property_id']
              for suffix in suffix_list:
                full_id = prop['id']+'_'+suffix
                if full_id not in current_list:
                  current_list.append(full_id)
        ps_property = getattr(base, '_categories', None)
        if type(ps_property) in (type(()), type([])):
          cat_dict_list = []
          for category in ps_property:
            if category not in current_list:
              current_list.append(category)
      return current_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstancePropertyMap' )
    def getInstancePropertyMap(self):
      """
      Returns the list of properties which are specific to the portal type.

      We do this by creating a temp object at the root of the portal
      and invoking propertyMap
      """
      # Access the factory method for temp object by guessing it
      # according to ERP5 naming conventions (not very nice)
      factory_method_id = self.factory.replace('add', 'newTemp', 1)
      if not factory_method_id.startswith('newTemp'):
        raise
      factory_method = getattr(Products.ERP5Type.Document, factory_method_id)
      id = "some_very_unlikely_temp_object_id_which_should_not_exist"
      portal = self.portal_url.getPortalObject()
      portal_ids = portal.objectIds()
      while id in portal_ids:
        id = id + "d"
      return factory_method(portal, id).propertyMap()

    security.declarePrivate('updateLocalRolesOnSecurityGroups')
    def updateLocalRolesOnSecurityGroups(self, ob, user_name=None,
                                         reindex=True):
      """
        Assign Local Roles to Groups on object 'ob', based on Portal Type Role
        Definitions and "ERP5 Role Definition" objects contained inside 'ob'.
      """
      #FIXME We should check the type of the acl_users folder instead of
      #      checking which product is installed.
      if user_name is None:
        # First try to guess from the owner
        try:
          user_name = ob.getOwnerInfo()['id']
        except (AttributeError, TypeError):
          pass
      if user_name is None:
        if ERP5UserManager is not None:
          # We use id for roles in ERP5Security
          user_name = getSecurityManager().getUser().getId()
        elif NuxUserGroups is not None:
          user_name = getSecurityManager().getUser().getUserName()
        else:
          raise RuntimeError, 'Product "ERP5Security" was not found on'\
                'your setup. '\
                'Please install it to benefit from group-based security'

      # Retrieve applicable roles
      role_mapping = self.getFilteredRoleListFor(ob=ob)

      # Create an empty local Role Definition dict
      role_category_list_dict = {}

      # Fill it with explicit local roles defined as subobjects of current
      # object
      if getattr(aq_base(ob), 'isPrincipiaFolderish', 0):
        for roledef in ob.objectValues(spec = 'ERP5 Role Definition'):
          role_category_list_dict.setdefault(roledef.getRoleName(), []).append(
                            {
                                'category_order'  : ['agent'],
                                'agent'           : roledef.getAgentList()
                            })

      # Then parse role mapping
      for role_text, definition_list in role_mapping.items():
        # For each role definition, we look for the base_category_script
        # and try to use it to retrieve the values for the base_category list
        for definition in definition_list:
          # get the list of base_categories that are statically defined
          static_base_category_list = [x.split('/', 1)[0]
                                       for x in definition['category']]
          # get the list of base_categories that are to be fetched through the
          # script
          dynamic_base_category_list = [x for x in 
             definition['base_category'] if x not in static_base_category_list]
          # get the aggregated list of base categories, to preserve the order
          category_order_list = []
          category_order_list.extend(definition['base_category'])
          for bc in static_base_category_list:
            if bc not in category_order_list:
              category_order_list.append(bc)

          # get the script and apply it if dynamic_base_category_list is not
          # empty
          if len(dynamic_base_category_list) > 0:
            base_category_script_id = definition['base_category_script']
            base_category_script = getattr(ob, base_category_script_id, None)
            if base_category_script is not None:
              # call the script, which should return either a dict or a list of
              # dicts
              category_result = base_category_script(
                                        dynamic_base_category_list,
                                        user_name,
                                        ob,
                                        ob.getPortalType() )
              # If we decide in the script that we don't want to update the
              # security for this object, we can just have it return None
              # instead of a dict or list of dicts
              if category_result is None:
                continue
            else:
              raise RuntimeError, 'Script %s was not found to fetch values for'\
                      ' base categories : %s' % (base_category_script_id,
                                            ', '.join(dynamic_base_category_list))
          else:
            # no base_category needs to be retrieved using the script, we use
            # a list containing an empty dict to trick the system into
            # creating one category_value_dict (which will only use statically
            # defined categories)
            category_result = [{}]

          # Prepare definition dict once only
          category_definition_dict = {}
          for c in definition['category']:
            bc, value = c.split('/', 1)
            category_definition_dict.setdefault(bc, []).append(value)
          # Now create role dict for each roles
          for role in role_text.split(';'):
            role = role.strip()
            if isinstance(category_result, dict):
              # category_result is a dict (which provide group IDs directly)
              # which represents of mapping of roles, security group IDs
              # XXX explain that this is for providing user IDs mostly
              role_category_list_dict.setdefault(role, category_result)
            else:
              # category_result is a list of dicts that represents the resolved
              # categories we create a category_value_dict from each of these
              # dicts aggregated with category_order and statically defined
              # categories
              role_category_list = role_category_list_dict.setdefault(role, [])
              for category_dict in category_result:
                category_value_dict = {'category_order':category_order_list}
                category_value_dict.update(category_dict)
                category_value_dict.update(category_definition_dict)
                role_category_list.append(category_value_dict)

      # Generate security group ids from category_value_dicts
      role_group_id_dict = {}
      group_id_generator = getattr( ob,
                             ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT,
                             None )
      if group_id_generator is None:
        raise RuntimeError, '%s script was not found' % \
                              ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT
      for role, value_list in role_category_list_dict.items():
        if isinstance(value_list, dict):
          # value_list is a dict (which provide group IDs directly)
          # This is used by acquisition scripts
          role_group_id_dict.setdefault(role, []).extend(value_list.get(role, []))
          continue
        role_group_dict = {}
        for category_dict in value_list:
          group_id = group_id_generator(**category_dict) # category_order is passed in the dict
                                                         # apparently, python can handle it
                                                         # even though category_order is not a named variable
                                                         # of the script
          # If group_id is not defined, do not use it
          if group_id not in (None, ''):
            if isinstance(group_id, str):
              # Single group is defined (this is usually for group membership)
              # DEPRECATED due to cartesian product requirement
              role_group_dict[group_id] = 1
            else:
              # Multiple groups are defined (list of users
              # or list of group IDs resulting from a cartesian product)
              for user_id in group_id:
                role_group_dict[user_id] = 1
        role_group_id_dict.setdefault(role, []).extend(role_group_dict.keys())

      # Switch index from role to group id
      group_id_role_dict = {}
      for role, group_list in role_group_id_dict.items():
        for group_id in group_list:
          group_id_role_dict.setdefault(group_id, []).append(role)

      # Update role assignments to groups
      if ERP5UserManager is not None: # Default implementation
        # Clean old group roles
        old_group_list = ob.get_local_roles()
        ob.manage_delLocalRoles([x[0] for x in old_group_list])
        # Save the owner
        for group, role_list in old_group_list:
          if 'Owner' in role_list:
            if not group_id_role_dict.has_key(group):
              group_id_role_dict[group] = ('Owner',)
            else:
              group_id_role_dict[group].append('Owner')
        # Assign new roles
        for group, role_list in group_id_role_dict.items():
          ob.manage_addLocalRoles(group, role_list)
      else: # NuxUserGroups implementation
        # Clean old group roles
        old_group_list = ob.get_local_group_roles()
        # We duplicate role settings to mimic PAS
        ob.manage_delLocalGroupRoles([x[0] for x in old_group_list])
        ob.manage_delLocalRoles([x[0] for x in old_group_list])
        # Save the owner
        for group, role_list in old_group_list:
          if 'Owner' in role_list:
            if not group_id_role_dict.has_key(group):
              group_id_role_dict[group] = ('Owner',)
            else:
              group_id_role_dict[group].append('Owner')
        # Assign new roles
        for group, role_list in group_id_role_dict.items():
          # We duplicate role settings to mimic PAS
          ob.manage_addLocalGroupRoles(group, role_list)
          ob.manage_addLocalRoles(group, role_list)
      # Make sure that the object is reindexed
      if reindex:
        ob.reindexObjectSecurity()

    # XXX compat. alias
    security.declareProtected(Permissions.ModifyPortalContent,
                              'assignRoleToSecurityGroup')
    assignRoleToSecurityGroup = updateLocalRolesOnSecurityGroups

    security.declarePublic('getFilteredRoleListFor')
    def getFilteredRoleListFor(self, ob=None, **kw):
        """
        Return a mapping containing of all roles applicable to the
        object against user.
        """
        # This is only for backward-compatibility. The keyword parameter
        # took object instead of ob in the old implementation.
        if ob is None:
          ob = kw.get('object')

        portal = self.portal_url.getPortalObject()
        if ob is None:
          folder = portal
        else:
          folder = aq_parent(ob)
          # Search up the containment hierarchy until we find an
          # object that claims it's a folder.
          while folder is not None:
            if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
              # found it.
              break
            else:
              folder = aq_parent(folder)

        ec = createExprContext(folder, portal, ob)
        roles = []
        append = roles.append
        info = ori(self, folder, ob)

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
    def _filterRoleList(self, append, ob, info, ec):
        r = ob.getRoleList(info)
        if r and not isinstance(r[0], dict):
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

    def reorderActions(self, REQUEST=None):
      """Reorder actions according to their priorities."""
      new_actions = self._cloneActions()
      new_actions.sort(lambda x,y: cmp(x.getPriority(), y.getPriority()))
      self._actions = tuple( new_actions )

      if REQUEST is not None:
        return self.manage_editActionsForm(REQUEST,
            manage_tabs_message='Actions reordered.')

InitializeClass( ERP5TypeInformation )

def manage_addERP5TIForm(self, REQUEST):
  ' form to add an ERP5 Type Information '
  return self._addTIForm(
      self, REQUEST,
      add_meta_type=ERP5TypeInformation.meta_type,
      types=self.listDefaultTypeInformation())


# Dynamic patch
Products.CMFCore.TypesTool.typeClasses.append(
                          {'class':ERP5TypeInformation,
                           'name':ERP5TypeInformation.meta_type,
                           'action':'manage_addERP5TIForm',
                           'permission':'Manage portal'}, )
Products.CMFCore.TypesTool.TypesTool.manage_addERP5TIForm = manage_addERP5TIForm


# vim: filetype=python syntax=python shiftwidth=2 
