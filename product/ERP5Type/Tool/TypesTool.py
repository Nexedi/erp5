##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Julien Muchembled <jm@nexedi.com>
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

import imp, sys, warnings
import inspect
from itertools import chain
import zope.interface
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder as OFSFolder
import transaction
from Products.CMFCore import TypesTool as CMFCore_TypesToolModule
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from zLOG import LOG, WARNING, PANIC
from Products.ERP5Type.interfaces import ITypeProvider, ITypesTool
from Products.ERP5Type.dynamic.portal_type_class import synchronizeDynamicModules
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable


class ComposedObjectIds(object):
  """Sequence type used to iterate efficiently over a union of folders

  Returned values are ids of contained objects.
  This type should used instead of building a simple list from the concatenation
  of multiple calls on objectIds.

  Note this class even implements '__contains__', which makes:
    'some_id' in ComposedObjectIds([container])
  faster than:
    'some_id' in container.objectIds()

  XXX Is it only useful for TypesTool ?
      If not, this should it be moved in another place, like ERP5Type.Utils
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, container_list):
    self._container_list = container_list

  def __contains__(self, item):
    for container in self._container_list:
      if container.has_key(item):
        return True
    return False

  def __iter__(self):
    return chain(*[container.objectIds() for container in self._container_list])

  def __len__(self):
    return sum(map(len, self._container_list))

  def __getitem__(self, item):
    for container in self._container_list:
      count = len(container)
      if item < count:
        return container.objectIds()[item]
      item -= count
    raise IndexError


CMFCore_TypesTool = CMFCore_TypesToolModule.TypesTool

class TypeProvider(BaseTool, CMFCore_TypesTool):
  """Provides portal content types
  """
  zope.interface.implements(ITypeProvider)


class TypesTool(TypeProvider):
  """Provides a configurable registry of portal content types
  """
  id = 'portal_types'
  meta_type = 'ERP5 Types Tool'
  portal_type = 'Types Tool'
  allowed_types = ()

  zope.interface.implements(ITypesTool)

  # TODO: UI to configure this is missing
  type_provider_list = ( )

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _isBootstrapRequired(self):
    if not self.has_key('Standard Property'):
      return True
    # bootstrap is not required, but we may have a few bugfixes to apply
    # so that the user can upgrade Business Templates
    property_sheet_type = self.get('Property Sheet')
    try:
      if property_sheet_type.aq_base.type_class != 'PropertySheet':
        property_sheet_type.type_class = 'PropertySheet'
    except AttributeError:
      pass
    try:
      script = self.getPortalObject().portal_workflow \
        .dynamic_class_generation_interaction_workflow.scripts \
        .DynamicClassGeneration_resetDynamicDocuments
      new = '.resetDynamicDocumentsOnceAtTransactionBoundary('
      if new not in script._body:
        script._body = script._body.replace('.resetDynamicDocuments(', new)
        script._makeFunction()
    except AttributeError:
      pass
    return False

  def _bootstrap(self):
    from Products.ERP5.ERP5Site import ERP5Generator
    ERP5Generator.bootstrap(self, 'erp5_core', 'PortalTypeTemplateItem', (
      'Business Template',
      'Standard Property',
      'Acquired Property',
      # the following ones are required to upgrade an existing site
      'Category Property',
      # the following is needed to bootstrap Catalog Tool and default catalog
      'Catalog Tool',
    ))
    ERP5Generator.bootstrap_allow_type(self, 'Catalog Tool')

  def listContentTypes(self, container=None):
    """List content types from all providers
    """
    if container is not None:
      # XXX Slow legacy implementation. Is 'container_list' parameter useful ?
      return CMFCore_TypesTool.listContentTypes(self, container)
    object_list = [self]
    _getOb = self.getPortalObject()._getOb
    for provider in self.type_provider_list:
      provider_value = _getOb(provider, None)
      if provider_value:
        object_list.append(provider_value)
    return ComposedObjectIds(object_list)

  def listTypeInfo(self, container=None):
    """List type information from all providers
    """
    listTypeInfo = CMFCore_TypesTool.listTypeInfo
    type_info_list = listTypeInfo(self, container=container)
    _getOb = self.getPortalObject()._getOb
    for provider in self.type_provider_list:
      provider_value = _getOb(provider, None)
      if provider_value is not None:
        type_info_list += listTypeInfo(provider_value, container=container)
    return type_info_list

  def _aq_dynamic(self, id):
    """Get a type information from a provider
    """
    result = BaseTool._aq_dynamic(self, id)
    if result is not None:
      return result

    if id in self.type_provider_list:
      return None

    default = []
    for provider in self.type_provider_list:
      provider_value = getattr(self, provider, None)
      if provider_value is not None:
        ob = provider_value._getOb(id, default=default)
        if ob is not default:
          return ob
    return None

  security.declarePrivate('getActionListFor')
  def getActionListFor(self, ob=None):
    """Return all actions applicable to the object"""
    if ob is not None:
      type_info = self.getTypeInfo(ob)
      if type_info is not None:
        return type_info.getActionList()
    return ()

  def getTypeInfo(self, *args):
    if not args:
       return BaseTool.getTypeInfo(self)
    portal_type, = args
    if not isinstance(portal_type, basestring):
      try:
        portal_type = aq_base(portal_type).getPortalType()
      except AttributeError:
        return None
    return getattr(self, portal_type, None)

  security.declareProtected(Permissions.AccessContentsInformation, 'getPortalTypeClass')
  def getPortalTypeClass(self, context, temp=False):
    """
    Infer a portal type class from the context.
    Context can be a portal type string, or an object, or a class.

    This is the proper API to retrieve a portal type class, and no one
    should hack anything anywhere else.
    """
    portal_type = None
    if isinstance(context, type):
      if context.__module__ in ('erp5.portal_type', 'erp5.temp_portal_type'):
        portal_type = context.__name__
      else:
        portal_type = getattr(context, 'portal_type', None)
    elif isinstance(context, str):
      portal_type = context
    else:
      portal_type = getattr(context, 'portal_type', None)

    if portal_type is not None:
      import erp5
      if temp:
        module = erp5.temp_portal_type
      else:
        module = erp5.portal_type
      return getattr(module, portal_type, None)

  def _getTypeList(self, component_portal_type, fs_type_list):
    portal = self.getPortalObject()
    version_priority_set = set(portal.getVersionPriorityNameList())

    # objectValues should not be used for a large number of objects, but
    # this is only done upon reset, moreover using the Catalog is too risky
    # as it lags behind and depends upon objects being reindexed
    type_set = set(fs_type_list)
    for component in portal.portal_components.objectValues(portal_type=component_portal_type):
      # Only consider modified or validated states as state transition will
      # be handled by component_validation_workflow which will take care of
      # updating the registry
      validation_state_tuple = component.getValidationState()
      if validation_state_tuple in ('modified', 'validated'):
        version = component.getVersion(validated_only=True)
        # The versions should have always been set on ERP5Site property
        # beforehand
        if version in version_priority_set:
          type_set.add(component.getReference(validated_only=True))

    return sorted(type_set)

  security.declareProtected(Permissions.AccessContentsInformation, 'getDocumentTypeList')
  def getDocumentTypeList(self):
    """
    Return a list of Document types (including filesystem and ZODB Component
    Documents) that can be used as Base classes
    """
    from Products.ERP5Type import document_class_registry
    return self._getTypeList(('Document Component', 'Tool Component'),
                             document_class_registry)

  security.declareProtected(Permissions.AccessContentsInformation, 'getMixinTypeList')
  def getMixinTypeList(self):
    """
    Return a list of class names that can be used as Mixins
    """
    from Products.ERP5Type import mixin_class_registry
    return self._getTypeList('Mixin Component', mixin_class_registry)

  security.declareProtected(Permissions.AccessContentsInformation, 'getInterfaceTypeList')
  def getInterfaceTypeList(self):
    """
    Return a list of class names that can be used as Interfaces
    """
    from Products.ERP5Type import interfaces
    return self._getTypeList(
      'Interface Component',
      [name for name, _ in inspect.getmembers(interfaces, inspect.isclass)])

  security.declareProtected(Permissions.ModifyPortalContent,
                            'resetDynamicDocumentsOnceAtTransactionBoundary')
  def resetDynamicDocumentsOnceAtTransactionBoundary(self):
    """
    Schedule a single reset at the end of the transaction, only once.
    The idea behind this is that a reset is (very) costly and that we want
    to do it as little often as possible.
    Moreover, doing it twice in a transaction is useless (but still twice
    as costly).
    And lastly, WorkflowMethods are not yet clever enough to allow this
    possibility, as they schedule interactions depending on an instance path:
    calling two times a setter on two different portal types during the
    same transaction would call twice resetDynamicDocuments without this
    TransactionalVariable check
    """
    tv = getTransactionalVariable()
    key = 'TypesTool.resetDynamicDocumentsOnceAtTransactionBoundary'
    if key not in tv:
      tv[key] = None
      transaction.get().addBeforeCommitHook(self.resetDynamicDocuments)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'resetDynamicDocuments')
  def resetDynamicDocuments(self):
    """Resets all dynamic documents: force reloading erp.* classes

    WARNING: COSTLY! Please double-check that
    resetDynamicDocumentsOnceAtTransactionBoundary can't be used instead.
    """
    synchronizeDynamicModules(self, force=True)

  def _finalizeMigration(self):
    """Compatibility code to finalize migration from CMF Types Tool"""
    portal = self.getPortalObject()
    old_types_tool = portal.__dict__[OldTypesTool.id]
    #self.Base_setDefaultSecurity()
    trash_tool = getattr(portal, 'portal_trash', None)
    if trash_tool is not None:
      LOG('OldTypesTool', WARNING, 'Move old portal_types into a trash bin.')
      portal._objects = tuple(i for i in portal._objects
                                if i['id'] != old_types_tool.id)
      portal._delOb(old_types_tool.id)
      #old_types_tool.id = self.id # Not possible to keep the original id
                                   # due to limitation of getToolByName
      trashbin = UnrestrictedMethod(trash_tool.newTrashBin)(self.id)
      trashbin._setOb(old_types_tool.id, old_types_tool)

# Compatibility code to access old "ERP5 Role Information" objects.
OldRoleInformation = imp.new_module('Products.ERP5Type.RoleInformation')
sys.modules[OldRoleInformation.__name__] = OldRoleInformation
from OFS.SimpleItem import SimpleItem
OldRoleInformation.RoleInformation = SimpleItem

def _eventLessSetObject(container):
  _setObject = container._setObject
  return lambda *args, **kw: _setObject(suppress_events=True, *args, **kw)

class OldTypesTool(OFSFolder):

  id = 'cmf_portal_types'

  def _migratePortalType(self, types_tool, old_type):
    import erp5
    BaseType = getattr(erp5.portal_type, 'Base Type')
    type_id = old_type.id
    if old_type.__class__ is not BaseType:
      LOG('OldTypesTool._migratePortalType', WARNING,
          "Can't convert %r (meta_type is %r)."
          % (old_type, old_type.meta_type))
      return
    new_type = BaseType(type_id, uid=None)
    _eventLessSetObject(types_tool)(type_id, new_type, set_owner=0)
    new_type = types_tool[type_id]
    def generateNewId():
      new_id = str(int(new_type.__dict__.get('last_id', 0)) + 1)
      new_type.last_id = new_id
      return new_id
    try:
      new_type.generateNewId = generateNewId
      new_type._setObject = _eventLessSetObject(new_type)
      for k, v in old_type.__dict__.iteritems():
        if k == '_actions':
          for action in v:
            new_type._importOldAction(action)
        elif k == '_roles':
          for role in v:
            new_type._importRole(role.__getstate__())
        elif k not in ('uid', 'isIndexable'):
          if k == '_property_domain_dict':
            v = {k: t.__class__(property_name=t.property_name,
                                domain_name=t.domain_name)
                 for k, t in v.iteritems()}
          setattr(new_type, k, v)
    finally:
      del new_type.generateNewId
      del new_type._setObject

  def _migrateTypesTool(self, parent):
    # 'parent' has no acquisition wrapper so migration must be done without
    # access to physical root. All activities are created with no leading '/'
    # in the path.
    LOG('OldTypesTool', WARNING, "Converting portal_types...")
    for object_info in parent._objects:
      if object_info['id'] == TypesTool.id:
        break
    types_tool = TypesTool()
    types_tool.__ac_local_roles__ = self.__ac_local_roles__.copy()
    setattr(parent, self.id, self)
    object_info['id'] = self.id
    del parent.portal_types
    _eventLessSetObject(parent)(TypesTool.id, types_tool, set_owner=0)
    types_tool = types_tool.__of__(parent)
    if not parent.portal_categories.hasObject('action_type'):
      # Required to generate ActionInformation.getActionType accessor.
      import erp5
      action_type = getattr(erp5.portal_type, 'Base Category')('action_type')
      action_type.uid = None
      parent.portal_categories._setObject(action_type.id, action_type)
    for type_info in self.objectValues():
      self._migratePortalType(types_tool, type_info)
    types_tool.activate()._finalizeMigration()
    LOG('OldTypesTool', WARNING, "... portal_types converted.")
    return types_tool

  def __of__(self, parent):
    base_self = aq_base(self) # Is it required ?
    if parent.__dict__.get(TypesTool.id) is not base_self:
      return OFSFolder.__of__(self, parent)
    return UnrestrictedMethod(base_self._migrateTypesTool)(parent)

# Change the CMFCore's TypesTool to automatically migrate to ERP5Type's
# TypesTool
CMFCore_TypesToolModule.TypesTool = OldTypesTool
