# -*- coding: utf-8 -*-
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

from __future__ import absolute_import
from six import string_types as basestring
from functools import partial
import zope.interface
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base, aq_inner, aq_parent
import Products
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import interfaces, Constraint, Permissions, PropertySheet
from Products.ERP5Type.Base import getClassPropertyList
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.Utils import deprecated, createExpressionContext
from Products.ERP5Type.ImmediateReindexContextManager import ImmediateReindexContextManager
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.dynamic.accessor_holder import getPropertySheetValueList, \
    getAccessorHolderList
import six

ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT = 'ERP5Type_asSecurityGroupId'
ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT_V2 = 'ERP5Type_asSecurityGroupIdSet'

from .TranslationProviderBase import TranslationProviderBase
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Accessor.Translation import TRANSLATION_DOMAIN_CONTENT_TRANSLATION
from zLOG import LOG, ERROR
from Products.CMFCore.exceptions import zExceptions_Unauthorized

@zope.interface.implementer(interfaces.ILocalRoleAssignor)
class LocalRoleAssignorMixIn(object):
    """Mixin class used by type informations to compute and update local roles
    """
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    security.declarePrivate('updateLocalRolesOnDocument')
    @UnrestrictedMethod
    def updateLocalRolesOnDocument(self, ob, user_name=None, reindex=True, activate_kw=()):
      """
        Assign Local Roles to Groups on object 'ob', based on Portal Type Role
        Definitions and "ERP5 Role Definition" objects contained inside 'ob'.
      """
      if user_name is None:
        # First try to guess from the owner
        owner = ob.getOwnerTuple()
        if owner:
          user_name = owner[1]
        else:
          for user_name, role_list in six.iteritems((ob.__ac_local_roles__ or {})):
            if 'Owner' in role_list:
              break
          else:
            user_name = getSecurityManager().getUser().getId()

      group_id_role_dict = {user_name: {'Owner'}}
      local_roles_group_id_group_id = {}
      # Merge results from applicable roles
      for role_generator in self.getFilteredRoleListFor(ob):
        local_roles_group_id = ''
        if getattr(role_generator, 'getLocalRoleGroupValue', None) is not None:
          # only some role generators like 'Role Information' support it
          local_role_group = role_generator.getLocalRoleGroupValue()
          if local_role_group is not None:
            # role definitions use category to classify different types of local roles
            # so use their categories' reference
            local_roles_group_id = local_role_group.getReference() or local_role_group.getId()
        for group_id, role_list \
                in six.iteritems(role_generator.getLocalRolesFor(ob, user_name)):
          group_id_role_dict.setdefault(group_id, set()).update(role_list)
          if local_roles_group_id:
            for role in role_list:
              # Feed local_roles_group_id_group_id with local roles assigned to a group
              local_roles_group_id_group_id.setdefault(local_roles_group_id, set()).update(((group_id, role),))

      ## Update role assignments to groups
      # Assign new roles
      ac_local_roles = {group: sorted(role_list)
        for group, role_list in six.iteritems(group_id_role_dict)
        if role_list}

      if ac_local_roles != ob.__ac_local_roles__:
        ob.__ac_local_roles__ = ac_local_roles
      if local_roles_group_id_group_id != getattr(ob, '__ac_local_roles_group_id_dict__', {}):
        if local_roles_group_id_group_id:
          ob.__ac_local_roles_group_id_dict__ = local_roles_group_id_group_id
        else:
          try:
            del ob.__ac_local_roles_group_id_dict__
          except AttributeError:
            pass

      ## Make sure that the object is reindexed if modified
      # XXX: Document modification detection assumes local roles are always
      # part of ob and not separate persistent objects.
      if reindex and ob._p_changed:
        ob.reindexObjectSecurity(activate_kw=dict(activate_kw))

    security.declarePrivate('getFilteredRoleListFor')
    def getFilteredRoleListFor(self, ob=None):
      """Return all role generators applicable to the object."""
      ec = None # createExpressionContext is slow so we call it only if needed
      for role in self.getRoleInformationList():
        if ec is None:
          ec = createExpressionContext(ob)
        if role.testCondition(ec):
          yield role

      # Return also explicit local roles defined as subobjects of the document
      if getattr(aq_base(ob), 'isPrincipiaFolderish', 0) and \
         self.allowType('Role Definition'):
        for role in ob.objectValues(spec='ERP5 Role Definition'):
          if role.getRoleName():
            yield role

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getRoleInformationList')
    def getRoleInformationList(self):
      """Return all Role Information objects stored on this portal type"""
      return self.objectValues(meta_type='ERP5 Role Information')

    security.declareProtected(Permissions.ModifyPortalContent,
                              'updateRoleMapping')
    def updateRoleMapping(self, REQUEST=None, form_id='', priority=3):
      """Update the local roles in existing objects.
      """
      self.getPortalObject().portal_catalog._searchAndActivate(
        'updateLocalRolesOnSecurityGroups',
        restricted=False,
        method_kw={
          'activate_kw': {
            'priority': priority,
          },
        },
        activate_kw={
          'priority': priority,
          # XXX: Tag is just for easier manual lookup in activity tables.
          'tag': self.id + '.updateRoleMapping',
        },
        portal_type=self.id,
      )
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(
          self.absolute_url_path() + '/' + form_id +
          '?portal_status_message=Updating%20local%20roles',
        )

    def _importRole(self, role_property_dict):
      """Import a role from a BT or from an old portal type"""
      import erp5
      RoleInformation = getattr(erp5.portal_type, 'Role Information')
      role = RoleInformation(self.generateNewId())
      for k, v in six.iteritems(role_property_dict):
        if k == 'condition':
          if isinstance(v, Expression):
            v = v.text
          if not v:
            continue
          v = Expression(v)
        elif k == 'priority':
          continue
        elif k == 'id':
          k, v = 'role_name', tuple(x.strip() for x in v.split(';'))
        elif k in ('base_category', 'category'):
          k, v = 'role_' + k, tuple(y for y in (x.strip() for x in v) if y)
        elif k == 'base_category_script':
          k = 'role_base_category_script_id'
        setattr(role, k, v)
      role.uid = None
      return self[self._setObject(role.id, role, set_owner=0)]

InitializeClass(LocalRoleAssignorMixIn)

@zope.interface.implementer(interfaces.IActionContainer)
class ERP5TypeInformation(XMLObject,
                          FactoryTypeInformation,
                          LocalRoleAssignorMixIn,
                          TranslationProviderBase):
    """
    ERP5 Types are based on FactoryTypeInformation

    The most important feature of ERP5Types is programmable acquisition which
    allows defining attributes which are acquired through categories.

    Another feature is to define the way attributes are stored (localy,
    database, etc.). This allows combining multiple attribute sources
    in a single object. This feature will be in reality implemented
    through PropertySheet classes (TALES expressions)

    TODO:
    - add a warning for legacy groups which are no longer used
    - move groups of portal types to categories
      (now that we have portal types of portal types)
    """

    portal_type = 'Base Type'
    meta_type = 'ERP5 Base Type'

    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.BaseType, )

    acquire_local_roles = False
    property_sheet_list = ()
    base_category_list = ()
    workflow_list = ()
    init_script = ''
    product = 'ERP5Type'
    hidden_content_type_list = ()
    permission = ''

    def __init__(self, id, **kw):
      XMLObject.__init__(self, id)
      if 'meta_type' in kw:
        kw.setdefault('content_meta_type', kw.pop('meta_type'))
      if 'icon' in kw:
        kw.setdefault('content_icon', kw.pop('icon'))
      self.__dict__.update(kw)

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
      'alarm', 'rule', 'constraint', 'property',
      # ERP5 UBM (5 Classes)
      'resource', 'node', 'item',
      'path', # movement is generated from all *_movement group above.
      # Documents need to have portal types associated to them
      # just to be able to spawn temporary objects with the same behavior
      'abstract',
      # Types defining other types: it includes Base Type but also
      # portal types of portal types
      'type_definition',
      # Trade
      'discount', 'payment_condition', 'payment_node',
      'supply', 'supply_path', 'inventory_movement',
      'delivery', 'delivery_movement',
      'order', 'order_movement',
      'open_order',
      'container', 'container_line',
      'inventory',
      # Different Aspects of Supplier-Customer relation
      'sale', 'purchase', 'internal',
      # PDM
      'transformation', 'variation', 'sub_variation',
      'product', 'service', 'model_path',
      # Accounting
      'accounting_transaction', 'accounting_movement',
      'invoice', 'invoice_movement', 'balance_transaction_line',
      # CRM
      'event', 'ticket',
      'interface_post', # object used to track exchanges in/out of ERP5
      'payment_request',
      # DMS
      'document', 'web_document', 'file_document', 'embedded_document',
      'recent_document', 'my_document', 'template_document',
      'crawler_index',
      'post',
      # Solvers and simulation
      'divergence_tester', 'target_solver', 'delivery_solver',
      'amount_generator',  'amount_generator_line', 'amount_generator_cell',
      # Business Processes
      'trade_model_path', 'business_link', 'business_process',
      # Movement Group
      'movement_group',
      # Calendar
      'calendar',
      'calendar_period',
      # Project
      'project',
      # budget
      'budget_variation',
      # Module
      'module',
      # Document related to a person's assignment or career step
      'personal_item',
      # Base
      'entity', 'login',
      # Core
      'domain',
      # Wendelin
      'device',
      'device_configuration',
      'data_configuration',
      'data_descriptor',
      'data_sink',
      # LEGACY - needs a warning - XXX-JPS
      'tax_movement',
    )
    group_list = ()

    security.declarePublic('allowType')
    def allowType(self, contentType):
      """Test if objects of 'self' can contain objects of 'contentType'
      """
      return (not self.getTypeFilterContentType()
              or contentType in self.getTypeAllowedContentTypeList())

    #
    #   Acquisition editing interface
    #

    security.declarePrivate('_guessMethodAliases')
    def _guessMethodAliases(self):
        """ Override this method to disable Method Aliases in ERP5.
        """
        self.setMethodAliases({})
        return 1

    # security is declared by superclass
    def queryMethodID(self, alias, default=None, context=None):
        """ Query method ID by alias.

        In ERP5 we don't do aliases.
        """
        return default

    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed(self, container):
      """Test if user is allowed to create an instance in the given container
      """
      permission = self.permission or 'Add portal content'
      return getSecurityManager().checkPermission(permission, container)

    security.declarePublic('constructTempInstance')
    def constructTempInstance(self, container, id, *args, **kw ):
      """
      All ERP5Type.Document.newTempXXXX are constructTempInstance methods
      """
      return self.constructInstance(container, id, temp_object=1, *args, **kw)

    security.declarePublic('constructInstance')
    def constructInstance(self, container, id, created_by_builder=0,
                          temp_object=0, compute_local_role=None,
                          notify_workflow=True, is_indexable=None,
                          activate_kw=None, reindex_kw=None,
                          immediate_reindex=False, **kw):
      """
      Build a "bare" instance of the appropriate type in
      'container', using 'id' as its id.
      Call the init_script for the portal_type.

      immediate_reindex (bool, ImmediateReindexContextManager)
        Immediately (=during current transaction) reindex created document, so
        it is possible to find it in catalog before transaction ends.

        If a ImmediateReindexContextManager instance is given, a context (in
        python sense) must have been entered with it, and indexation will
        occur when that context is exited, allowing further changes before
        first indexation (ex: workflow state change, property change).

      Returns the object.
      """
      if compute_local_role is None:
        # If temp object, set to False
        compute_local_role = not temp_object
      if not temp_object and not self.isConstructionAllowed(container):
        raise AccessControl_Unauthorized('Cannot create %s' % self.getId())

      portal = container.getPortalObject()
      klass = portal.portal_types.getPortalTypeClass(
          self.getId(),
          temp=temp_object)
      base_ob = klass(id)
      assert base_ob.portal_type == self.getId()
      ob = base_ob.__of__(container)

      if temp_object:
        # Setup only Owner local role on Document like
        # container._setObject(set_owner=True) does.
        user = getSecurityManager().getUser()
        if user is not None:
          user_id = user.getId()
        else:
          user_id = 'Anonymous Owner'
        ob.manage_setLocalRoles(user_id, ['Owner'])
      else:
        if activate_kw is not None:
          ob.setDefaultActivateParameterDict(activate_kw)
        if reindex_kw is not None:
          ob.setDefaultReindexParameterDict(reindex_kw)
        if is_indexable is not None:
          base_ob.isIndexable = is_indexable
        container._setObject(id, base_ob)
        # if no activity tool, the object has already an uid
        if getattr(base_ob, 'uid', None) is None:
          ob.uid = portal.portal_catalog.newUid()

      if compute_local_role:
        # Do not reindex object because it's already done by manage_afterAdd
        self.updateLocalRolesOnDocument(ob, reindex=False)

      if notify_workflow:
        # notify workflow after generating local roles, in order to prevent
        # Unauthorized error on transition's condition
        workflow_tool = portal.portal_workflow
        if workflow_tool is not None:
          for workflow in workflow_tool.getWorkflowValueListFor(ob):
            workflow.notifyCreated(ob)

      if not temp_object:
        init_script = self.getTypeInitScriptId()
        if init_script:
          # Acquire the init script in the context of this object
          getattr(ob, init_script)(created_by_builder=created_by_builder,
                                   edit_kw=kw)

      if kw:
        ob._edit(force_update=1, **kw)

      if not temp_object and immediate_reindex is not None:
        # As we just created ob, we assume the whole subtree is of a
        # reasonable size and hence can be walked in current transaction.
        # Subtree may come from:
        # - acquired setter (ex: address on a Person which actually exists on
        #   a subdocument), which should be in very limited quantity
        # - type-based init script, which will have to delegate any
        #   large-document creation needs to later transactions
        #   (activities). Or just not request immediate indexation.
        # - if ImmediateReindexContextManager is used, anything until
        #   context manager exits.
        method = ob._reindexOnCreation
        if activate_kw is not None:
          if reindex_kw is None:
            reindex_kw = {}
          reindex_kw.setdefault('activate_kw', {}).update(activate_kw)
        if reindex_kw is not None:
          method = partial(method, **reindex_kw)
        if isinstance(immediate_reindex, ImmediateReindexContextManager):
          immediate_reindex.append(method)
        elif immediate_reindex:
          # Immediately reindexing document that we just created is safe, as no
          # other transaction can by definition see it, so there cannot be a race
          # condition leading to stale catalog content.
          method()
      return ob

    def _getPropertyHolder(self):
      import erp5.portal_type as module
      return getattr(module, self.getId())

    # The following methods are needed before there are generated.

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTypePropertySheetList')
    def getTypePropertySheetList(self):
      """Getter for 'type_property_sheet' property"""
      return list(self.property_sheet_list)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTypeBaseCategoryList')
    def getTypeBaseCategoryList(self):
      """Getter for 'type_base_category' property"""
      return list(self.base_category_list)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTypeWorkflowList')
    def getTypeWorkflowList(self):
      """Getter for 'type_workflow' property"""
      return list(self.workflow_list)

    def _setTypeWorkflowList(self, type_workflow_list):
      self.workflow_list = type_workflow_list

    security.declareProtected(Permissions.ModifyPortalContent,
                              'setTypeWorkflowList')
    def setTypeWorkflowList(self, type_workflow_list):
      """Setter for 'type_workflow' property"""
      # We use 'sorted' below to keep an order in the workflow list. Without
      # this line, the actions can have different order depending on the order
      # set during the installation or later. This is bad!
      # It might not be the ideal solution, if you need to have the workflow
      # defined in a specific order. Then, your new implementation should use
      # indexes on workflows as in portal types action's priority.
      # Note: 'sorted' also convert a tuple or a set to a list
      self._setTypeWorkflowList(sorted(type_workflow_list))

    def getTypePropertySheetValueList(self):
      type_property_sheet_list = self.getTypePropertySheetList()
      if not type_property_sheet_list:
        return []

      return getPropertySheetValueList(self.getPortalObject(),
                                       type_property_sheet_list)

    def getAccessorHolderList(self):
      type_property_sheet_value_list = self.getTypePropertySheetValueList()
      if not type_property_sheet_value_list:
        return []

      return getAccessorHolderList(self.getPortalObject(),
                                   self.getPortalType(),
                                   type_property_sheet_value_list)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getRecursivePropertySheetValueList')
    def getRecursivePropertySheetValueList(self):
      """
      Get all the Property Sheets for this Portal Type, not only the one set on
      'type_property_sheet' property but also the ones defined on
      'property_sheets' property on each parent classes.
      """
      import erp5.portal_type
      portal_type_class = getattr(erp5.portal_type, self.getId())
      portal_type_class.loadClass()

      # XXX-arnau: There should be no need of checking this property (IOW
      # checking the MRO should be enough), but this is not enough for Portal
      # Types Accessor Holder (erp5.accessor_holder.portal_type), used by
      # Preferences for example (defining getAccessorHolderList() which
      # returns a single Accessor Holder from several Property
      # Sheets). Probably this behavior should be changed to have one Accessor
      # Holder per Property Sheet ?
      property_sheet_name_set = set(self.getTypePropertySheetList())

      for klass in portal_type_class.mro():
        if klass.__module__ == 'erp5.accessor_holder.property_sheet':
          property_sheet_name_set.add(klass.__name__)

      return getPropertySheetValueList(self.getPortalObject(),
                                       property_sheet_name_set)

    # XXX these methods, _baseGetTypeClass, getTypeMixinList,
    # getTypeAcquireLocalRole and getTypeInterfaceList, are required for a
    # bootstrap issue that the portal type class Base Type is required for
    # _aq_dynamic on Base Type. So surpress calling _aq_dynamic when obtaining
    # information required for generating a portal type class by declaring
    # these methods explicitly.
    def _baseGetTypeClass(self):
      return getattr(aq_base(self), 'type_class', None)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTypeFactoryMethodId')
    def getTypeFactoryMethodId(self):
      return getattr(aq_base(self), 'factory', ())

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTypeMixinList')
    def getTypeMixinList(self):
      return getattr(aq_base(self), 'type_mixin', ())

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTypeAcquireLocalRole')
    def getTypeAcquireLocalRole(self):
      return getattr(aq_base(self), 'acquire_local_roles', None)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTypeInterfaceList')
    def getTypeInterfaceList(self):
      return getattr(aq_base(self), 'type_interface', ())

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTypeClass')
    def getTypeClass(self):
      """Getter for type_class"""
      base = self._baseGetTypeClass()
      if base is None:
        # backwards compatibility: if the object has no
        # new-style type class, use the oldstyle factory attribute
        init_script = self.getTypeFactoryMethodId()
        if init_script and init_script.startswith('add'):
          base = init_script[3:]
          # and of course migrate the property,
          # avoiding any useless interaction/reindexation
          self.type_class = base
      return base

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstanceBaseCategoryList')
    def getInstanceBaseCategoryList(self):
      """ Return all base categories of the portal type """
      return list(self._getPropertyHolder()._categories)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstancePropertySet')
    def getInstancePropertySet(self):
      """
      Return all the properties of the Portal Type
      """
      portal = self.getPortalObject()
      cls = portal.portal_types.getPortalTypeClass(self.getId())
      return_set = set()
      for property_dict in cls.getAccessorHolderPropertyList(content=True):
        if property_dict['type'] == 'content':
          for suffix in property_dict['acquired_property_id']:
            return_set.add(property_dict['id'] + '_' + suffix)
        else:
          return_set.add(property_dict['id'])

        if property_dict['storage_id']:
          return_set.add(property_dict['storage_id'])

        if property_dict['translatable']:
          domain_dict = self.getPropertyTranslationDomainDict()
          domain = domain_dict.get(property_dict['id'])
          if domain is None:
            continue
          if domain.getDomainName() == TRANSLATION_DOMAIN_CONTENT_TRANSLATION:
            for language in portal.Localizer.get_languages():
              return_set.add('%s_translated_%s' %
                  (language.replace('-', '_'),
                   property_dict['id']))

      return return_set

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstancePropertyAndBaseCategorySet')
    def getInstancePropertyAndBaseCategorySet(self):
      """Return all the properties and base categories of the portal type. """
      # XXX: Hack until introspection methods are defined. At least, this works
      #      for portal_type whose properties are defined dynamically
      #      (e.g. temporary property sheets).
      #      See also AcquiredProperty._asPropertyMap
      cls = self.getPortalObject().portal_types.getPortalTypeClass(self.getId())
      return_set = self.getInstancePropertySet()
      for category in cls._categories:
        return_set.add(category)
        return_set.add(category + '_free_text')
      return return_set

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstancePropertyAndBaseCategoryList')
    @deprecated('getInstancePropertyAndBaseCategoryList is deprecated '
                'in favor of getInstancePropertyAndBaseCategorySet')
    def getInstancePropertyAndBaseCategoryList(self):
      """Return all the properties and base categories of the portal type"""
      return list(self.getInstancePropertyAndBaseCategorySet())

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstancePropertyMap')
    def getInstancePropertyMap(self):
      """
      Returns the list of properties which are specific to the portal type.
      """
      return self.__class__.propertyMap()

    security.declareProtected(Permissions.AccessContentsInformation,
                              'PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
      """Return keywords for "Find" tab in ZMI"""
      search_source_list = [self.getId(),
                            self.getTypeFactoryMethodId(),
                            self.getTypeAddPermission(),
                            self.getTypeInitScriptId()]
      search_source_list += self.getTypePropertySheetList()
      search_source_list += self.getTypeBaseCategoryList()
      search_source_list += self.getTypeWorkflowList()
      return ' '.join([_f for _f in search_source_list if _f])

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDefaultViewFor')
    def getDefaultViewFor(self, ob, view='view'):
      """Return the object that renders the default view for the given object
      """
      ec = createExpressionContext(ob)
      other_action = None
      for action in self.getActionList():
        if action['id'] == view or (action['category'] is not None and
                                    action['category'].endswith('_' + view)):
          if action.test(ec):
            break
        elif other_action is None:
          # In case that "view" (or "list") action is not present or not allowed,
          # find something that's allowed (of the same category, if possible).
          if action.test(ec):
            other_action = action
      else:
        action = other_action
        if action is None:
          raise AccessControl_Unauthorized(
            'No accessible views available for %r' % ob.getPath())

      target = action.cook(ec)['url'].strip().split(ec.vars['object_url'])[-1]
      if target.startswith('/'):
          target = target[1:]
      __traceback_info__ = self.getId(), target
      return ob.restrictedTraverse(target)

    security.declarePrivate('getCacheableActionList')
    def getCacheableActionList(self):
      """Return a cacheable list of enabled actions"""
      return [action.getCacheableAction()
              for action in self.getActionInformationList()
              if action.isVisible()]

    def _getActionList(self):
      action_list = self.getCacheableActionList()
      # This sort is a duplicate of calculation with what is done
      # on portal_actions.listFilteredActionsFor . But getDefaultViewFor
      # needs the sort here. This needs to be reviewed, because it is possible
      # to define in portal_actions some actions that will have higher
      # priorities than actions defined on portal types
      action_list.sort(key=lambda x:x['priority'])
      return action_list
    _getActionList = CachingMethod(_getActionList,
      id='getActionList',
      cache_factory='erp5_content_long',
      cache_id_generator=lambda method_id, *args: method_id)

    security.declarePrivate('getActionList')
    def getActionList(self):
      """Return the list of enabled actions from cache, sorted by priority"""
      return self._getActionList(self, scope=self.id)

    security.declareProtected(Permissions.ModifyPortalContent,
                              'clearGetActionListCache')
    def clearGetActionListCache(self):
      """Clear a cache of _getRawActionInformationList."""
      self._getActionList.delete(scope=self.id)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getActionInformationList')
    def getActionInformationList(self):
      """Return all Action Information objects stored on this portal type"""
      return self.objectValues(meta_type='ERP5 Action Information')

    def getIcon(self):
      try:
        return self.getTypeIcon()
      except AttributeError:
        # do not fail if the property is missing: getTypeIcon is used in the ZMI
        # and we always want to display the ZMI no matter what
        return ''

    def getTypeInfo(self, *args):
      if args:
        return self.getParentValue().getTypeInfo(*args)
      return XMLObject.getTypeInfo(self)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailablePropertySheetList')
    def getAvailablePropertySheetList(self):
      property_sheet_set = {k for k in PropertySheet.__dict__
                              if not k.startswith('_')}

      property_sheet_tool = self.getPortalObject().portal_property_sheets
      property_sheet_set.update(property_sheet_tool.objectIds())

      return sorted(property_sheet_set)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableConstraintList')
    def getAvailableConstraintList(self):
      return sorted(k for k in Constraint.__dict__
                      if k != 'Constraint' and not k.startswith('_'))

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableGroupList')
    def getAvailableGroupList(self):
      return sorted(self.defined_group_list)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableBaseCategoryList')
    def getAvailableBaseCategoryList(self):
        return sorted(self._getCategoryTool().getBaseCategoryList())

    #
    # XXX CMF compatibility
    #

    security.declareProtected(Permissions.ManagePortal,
                              'setPropertySheetList')
    @deprecated
    def setPropertySheetList(self, property_sheet_list):
      self._setTypePropertySheetList(property_sheet_list)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getHiddenContentTypeList')
    @deprecated
    def getHiddenContentTypeList(self):
      return self.getTypeHiddenContentTypeList(())

    # Compatibitility code for actions

    security.declareProtected(Permissions.AddPortalContent, 'addAction')
    @deprecated
    def addAction(self, id, name, action, condition, permission, category,
                  icon=None, visible=1, priority=1.0, REQUEST=None,
                  description=None):
      if isinstance(permission, basestring):
        permission = permission,
      if isinstance(action, str) and action[:7] not in ('string:', 'python:'):
        value = 'string:${object_url}/' + value
      self.newContent(portal_type='Action Information',
                      reference=id,
                      title=name,
                      action=action,
                      condition=condition,
                      permission_list=permission,
                      action_type=category,
                      icon=icon,
                      visible=visible,
                      float_index=priority,
                      description=description)

    security.declareProtected(Permissions.ModifyPortalContent, 'deleteActions')
    @deprecated
    def deleteActions(self, selections=(), REQUEST=None):
      action_list = self.listActions()
      self.manage_delObjects([action_list[x].id for x in selections])

    security.declarePrivate('listActions')
    @deprecated
    def listActions(self, info=None, object=None):
      """ List all the actions defined by a provider."""
      return sorted(self.getActionInformationList(),
                    key=lambda x: (x.getFloatIndex(), x.getId()))

    def _importOldAction(self, old_action):
      """Convert a CMF action to an ERP5 action

      This is used to update an existing site or to import a BT.
      """
      import erp5.portal_type
      ActionInformation = getattr(erp5.portal_type, 'Action Information')
      old_action = old_action.__getstate__()
      action_type = old_action.pop('category', None)
      action = ActionInformation(self.generateNewId())
      for k, v in six.iteritems(old_action):
        if k in ('action', 'condition', 'icon'):
          if not v:
            continue
          v = v.__class__(v.text)
        setattr(action, {'id': 'reference',
                         'priority': 'float_index',
                         'permissions': 'action_permission',
                        }.get(k, k), v)
      action.uid = None
      action = self[self._setObject(action.id, action, set_owner=0)]
      if action_type:
        action._setCategoryMembership('action_type', action_type)
      return action

    def _exportOldAction(self, action):
      """Convert an ERP5 action to a CMF action

      This is used to export a BT.
      """
      from Products.CMFCore.ActionInformation import ActionInformation
      old_action = ActionInformation(action.reference,
        category=action.getActionType(),
        priority=action.getFloatIndex(),
        permissions=tuple(action.getActionPermissionList()))
      for k, v in six.iteritems(action.__dict__):
        if k in ('action', 'condition', 'icon'):
          if not v:
            continue
          v = v.__class__(v.text)
        elif k in ('id', 'float_index', 'action_permission', 'reference'):
          continue
        setattr(old_action, k, v)
      return old_action

InitializeClass( ERP5TypeInformation )
