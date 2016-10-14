##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Dumazet <nicolas.dumazet@nexedi.com>
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import os
import inspect
import transaction

from Products.ERP5Type.mixin.temporary import TemporaryDocumentMixin
from Products.ERP5Type.Base import resetRegisteredWorkflowMethod
from . import aq_method_lock
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Utils import setDefaultClassProperties
from Products.ERP5Type import document_class_registry, mixin_class_registry
from Products.ERP5Type.dynamic.accessor_holder import createAllAccessorHolderList
from Products.ERP5Type.Accessor.Constant import Getter as ConstantGetter
from Products.ERP5Type.TransactionalVariable import TransactionalResource

from zLOG import LOG, ERROR, INFO, WARNING, PANIC

ACQUIRE_LOCAL_ROLE_GETTER_ID = '_getAcquireLocalRoles'
ACQUIRE_LOCAL_ROLE_GETTER_DICT = {
  acquire_local_role: type(
    'GetAcquireLocalRolesMixIn',
    (object, ),
    {
      ACQUIRE_LOCAL_ROLE_GETTER_ID: ConstantGetter(
        id=ACQUIRE_LOCAL_ROLE_GETTER_ID,
        key=None,
        value=acquire_local_role,
      ),
    },
  )
  for acquire_local_role in (False, True)
}

def _importClass(classpath):
  try:
    module_path, class_name = classpath.rsplit('.', 1)
    module = __import__(module_path, {}, {}, (module_path,))
    klass = getattr(module, class_name)

    # XXX is this required? (here?)
    setDefaultClassProperties(klass)
    InitializeClass(klass)

    return klass
  except StandardError:
    raise ImportError('Could not import document class ' + classpath)

# Loading Cache Factory portal type would generate the accessor holder
# for Cache Factory, itself defined with Standard Property thus
# loading the portal type Standard Property, itself defined with
# Standard Property and so on...
#
# NOTE: only the outer Property Sheets is stored in the accessor
# holder module
property_sheet_generating_portal_type_set = set()

# 'Types Tool' is required to access 'site.portal_types' and the
# former requires 'Base Type'. Thus, 'generating' is meaningful to
# avoid infinite recursion, whereas 'type_class' avoids accessing to
# portal_type
#
# For example, loading 'Types Tool' will try to load 'Types Tool' when
# accessing 'site.portal_types'. Therefore the inner one is just an
# import of 'Types Tool' class without any mixin, interface or
# Property Sheet to allow the outer (which will actually be stored in
# 'erp5.portal_type') to be fully generated.
#
# Solver Tool, as a TypeProvider, will also be required to access
# site.portal_types
core_portal_type_class_dict = {
  'Base Type':    {'type_class': 'ERP5TypeInformation',
                   'generating': False},
  'Solver Type':  {'type_class': 'SolverTypeInformation',
                   'generating': False},
  'Types Tool':   {'type_class': 'TypesTool',
                   'generating': False},
  'Solver Tool':  {'type_class': 'SolverTool',
                   'generating': False}
  }

def generatePortalTypeClass(site, portal_type_name):
  """
  Given a portal type, look up in Types Tool the corresponding
  Base Type object holding the definition of this portal type,
  and computes __bases__ and __dict__ for the class that will
  be created to represent this portal type

  Returns tuple with 4 items:
    - base_tuple: a tuple of classes to be used as __bases__
    - base_category_list: categories defined on the portal type
        (and portal type only: this excludes property sheets)
    - interface_list: list of zope interfaces the portal type implements
    - attribute dictionary: any additional attributes to put on the class
  """
  # LOG("ERP5Type.dynamic", INFO, "Loading portal type " + portal_type_name)

  global core_portal_type_class_dict

  portal_type_category_list = []
  attribute_dict = dict(portal_type=portal_type_name,
                        _categories=[],
                        constraints=[])

  if portal_type_name in core_portal_type_class_dict:
    if not core_portal_type_class_dict[portal_type_name]['generating']:
      # Loading the (full) outer portal type class
      core_portal_type_class_dict[portal_type_name]['generating'] = True
    else:
      # Loading the inner portal type class without any mixin,
      # interface or Property Sheet
      klass = _importClass(document_class_registry.get(
        core_portal_type_class_dict[portal_type_name]['type_class']))

      # LOG("ERP5Type.dynamic", INFO,
      #     "Loaded portal type %s (INNER)" % portal_type_name)

      # Don't do anything else, just allow to load fully the outer
      # portal type class
      return ((klass,), [], [], attribute_dict)

  # Do not use __getitem__ (or _getOb) because portal_type may exist in a
  # type provider other than Types Tool.
  portal_type = getattr(site.portal_types, portal_type_name, None)

  type_class = None

  if portal_type is not None:
    # type_class has a compatibility getter that should return
    # something even if the field is not set (i.e. Base Type object
    # was not migrated yet). It only works if factory_method_id is set.
    type_class = portal_type.getTypeClass()

    # The Tools used to have 'Folder' or None as type_class instead of
    # 'NAME Tool', so make sure the type_class is correct
    #
    # NOTE: under discussion so might be removed later on
    if portal_type_name.endswith('Tool') and type_class in ('Folder', None):
      type_class = portal_type_name.replace(' ', '')

    mixin_list = portal_type.getTypeMixinList()
    interface_list = portal_type.getTypeInterfaceList()
    portal_type_category_list = portal_type.getTypeBaseCategoryList()
    attribute_dict['_categories'] = portal_type_category_list[:]
    acquire_local_role = bool(portal_type.getTypeAcquireLocalRole())
  else:
    LOG("ERP5Type.dynamic", WARNING,
        "Cannot find a portal type definition for '%s', trying to guess..."
        % portal_type_name)

  # But if neither factory_init_method_id nor type_class are set on
  # the portal type, we have to try to guess, for compatibility.
  # Moreover, some tools, such as 'Activity Tool', don't have any
  # portal type
  if type_class is None:
    if portal_type_name in core_portal_type_class_dict:
      # Only happen when portal_types is empty (e.g. when creating a
      # new ERP5Site)
      type_class = core_portal_type_class_dict[portal_type_name]['type_class']
    else:
      # Try to figure out a coresponding document class from the
      # document side.  This can happen when calling newTempAmount for
      # instance:
      #  Amount has no corresponding Base Type and will never have one
      #  But the semantic of newTempXXX requires us to create an
      #  object using the Amount Document, so we promptly do it:
      type_class = portal_type_name.replace(' ', '')

    mixin_list = []
    interface_list = []
    acquire_local_role = True

  if type_class is None:
    raise AttributeError('Document class is not defined on Portal Type ' + \
                           portal_type_name)

  klass = None
  if '.' in type_class:
    type_class_path = type_class
  else:
    type_class_path = None

    # Skip any document within ERP5Type Product as it is needed for
    # bootstrapping anyway
    type_class_namespace = document_class_registry.get(type_class, '')
    if not (type_class_namespace.startswith('Products.ERP5Type') or
            portal_type_name in core_portal_type_class_dict):
      import erp5.component.document
      module = erp5.component.document.find_load_module(type_class)
      if module is not None:
        try:
          klass = getattr(module, type_class)
        except AttributeError:
          LOG("ERP5Type.dynamic", WARNING,
              "Could not get class '%s' in Component module %r, fallback on filesystem" %
              (type_class, module))

    if klass is None:
      type_class_path = document_class_registry.get(type_class)
      if type_class_path is None:
        raise AttributeError('Document class %s has not been registered:'
                             ' cannot import it as base of Portal Type %s'
                             % (type_class, portal_type_name))

  if klass is None:
    klass = _importClass(type_class_path)

  global property_sheet_generating_portal_type_set

  accessor_holder_list = []

  if portal_type_name not in property_sheet_generating_portal_type_set:
    # LOG("ERP5Type.dynamic", INFO,
    #     "Filling accessor holder list for portal_type " + portal_type_name)

    property_sheet_generating_portal_type_set.add(portal_type_name)
    try:
      # Initialize ZODB Property Sheets accessor holders
      accessor_holder_list = createAllAccessorHolderList(site,
                                                         portal_type_name,
                                                         portal_type,
                                                         klass)

      base_category_set = set(attribute_dict['_categories'])
      for accessor_holder in accessor_holder_list:
        base_category_set.update(accessor_holder._categories)
        attribute_dict['constraints'].extend(accessor_holder.constraints)

      attribute_dict['_categories'] = list(base_category_set)
    finally:
      property_sheet_generating_portal_type_set.remove(portal_type_name)

  # LOG("ERP5Type.dynamic", INFO,
  #     "Filled accessor holder list for portal_type %s (%s)" % \
  #     (portal_type_name, accessor_holder_list))

  mixin_class_list = []
  if mixin_list:
    # Only one Mixin class per ZODB Component (!= FS) where module_name ==
    # class_name, name ending with 'Mixin'.
    #
    # Rationale: same as Document/Interface; consistent naming; avoid a
    # registry like there used to be with FS.
    import erp5.component.mixin
    for mixin in mixin_list:
      mixin_module = erp5.component.mixin.find_load_module(mixin)
      mixin_class = None
      if mixin_module is not None:
        try:
          mixin_class = getattr(mixin_module, mixin)
        except AttributeError:
          LOG("ERP5Type.dynamic", WARNING,
              "Could not get class '%s' in Component module %r, fallback on filesystem" %
              (mixin, mixin_module))

      if mixin_class is None:
        mixin_class = _importClass(mixin_class_registry[mixin])

      mixin_class_list.append(mixin_class)

  base_class_list = [klass] + accessor_holder_list + mixin_class_list + [
    # _getAcquireLocalRoles is accessed by security machinery, so it needs to
    # be fast: make it a ConstantGetter while we have access to portal_type
    # configuration.
    ACQUIRE_LOCAL_ROLE_GETTER_DICT[acquire_local_role],
  ]

  interface_class_list = []
  if interface_list:
    # Filesystem Interfaces may have defined several Interfaces in one file
    # but only *one* Interface per ZODB Component where module_name ==
    # class_name, name starting with 'I'.
    #
    # Rationale: same as Document/Mixin; consistent naming; avoid a registry
    # like there used to be for Mixin or importing all class in
    # Products.ERP5Type.interfaces.__init__.py.
    import erp5.component.interface
    from Products.ERP5Type import interfaces as filesystem_interfaces
    for interface in interface_list:
      interface_module = erp5.component.interface.find_load_module(interface)
      interface_class = None
      if interface_module is not None:
        try:
          interface_class = getattr(interface_module, interface)
        except AttributeError:
          LOG("ERP5Type.dynamic", WARNING,
              "Could not get class '%s' in Component module %r, fallback on filesystem" %
              (interface, interface_module))

      if interface_class is None:
        interface_class = getattr(filesystem_interfaces, interface)

      interface_class_list.append(interface_class)

  if portal_type_name in core_portal_type_class_dict:
    core_portal_type_class_dict[portal_type_name]['generating'] = False

  attribute_dict['_restricted_setter_set'] = {method
        for ancestor in base_class_list
        for permissions in getattr(ancestor, '__ac_permissions__', ())
        if permissions[0] not in ('Access contents information',
                                  'Modify portal content')
        for method in permissions[1]
        if method.startswith('set')}

  attribute_dict['_restricted_getter_set'] = {method
        for ancestor in base_class_list
        for permissions in getattr(ancestor, '__ac_permissions__', ())
        if permissions[0] not in ('Access contents information', )
        for method in permissions[1]
        if method.startswith('get')}

  #LOG("ERP5Type.dynamic", INFO,
  #    "Portal type %s loaded with bases %s" \
  #        % (portal_type_name, repr(base_class_list)))

  return (tuple(base_class_list),
          portal_type_category_list,
          interface_class_list,
          attribute_dict)

def loadTempPortalTypeClass(portal_type_name):
  """
  Returns a class suitable for a temporary portal type

  This class will in fact be a subclass of erp5.portal_type.xxx, which
  means that loading an attribute on this temporary portal type loads
  the lazily-loaded parent class, and that any changes on the parent
  class will be reflected on the temporary objects.
  """
  import erp5.portal_type
  klass = getattr(erp5.portal_type, portal_type_name)

  return type("Temporary " + portal_type_name,
              (TemporaryDocumentMixin, klass), {})

last_sync = -1
_bootstrapped = set()
def synchronizeDynamicModules(context, force=False):
  """
  Allow resetting all classes to ghost state, most likely done after
  adding and removing mixins on the fly

  Most of the time, this reset is only hypothetic:
  * with force=False, the reset is only done if another node resetted
    the classes since the last reset on this node.
  * with force=True, forcefully reset the classes on the current node
    and send out an invalidation to other nodes
  """
  portal = context.getPortalObject()

  global last_sync
  if force:
    # hard invalidation to force sync between nodes
    portal.newCacheCookie('dynamic_classes')
    last_sync = portal.getCacheCookie('dynamic_classes')
  else:
    cookie = portal.getCacheCookie('dynamic_classes')
    if cookie == last_sync:
      # up to date, nothing to do
      return
    last_sync = cookie

  import erp5
  with aq_method_lock:
    # Thanks to TransactionalResource, the '_bootstrapped' global variable
    # is updated in a transactional way. Without it, it would be required to
    # restart the instance if anything went wrong.
    # XXX: In fact, TransactionalResource does not solve anything here, because
    #      portal cookie is unlikely to change and this function will return
    #      immediately, forcing the user to restart.
    #      This may not be so bad after all: it enables the user to do easily
    #      some changes that are required for the migration.
    if portal.id not in _bootstrapped and \
       TransactionalResource.registerOnce(__name__, 'bootstrap', portal.id):
      migrate = False
      from Products.ERP5Type.Tool.PropertySheetTool import PropertySheetTool
      from Products.ERP5Type.Tool.TypesTool import TypesTool
      from Products.ERP5Type.Tool.ComponentTool import ComponentTool
      from Products.ERP5Catalog.Tool.ERP5CatalogTool import ERP5CatalogTool
      try:
        for tool_class in TypesTool, PropertySheetTool, ComponentTool, ERP5CatalogTool:
          # if the instance has no property sheet tool, or incomplete
          # property sheets, we need to import some data to bootstrap
          # (only likely to happen on the first run ever)
          tool_id = tool_class.id
          tool = getattr(portal, tool_id, None)

          if tool is None:
            if tool_class == ERP5CatalogTool:
              # Wait till we find that SQL Catalog Tool is installed
              # Simpy said, we don't want  ERP5 Catalog Tool to be installed
              # from here. So, we come to 2 cases:
              # 1. Running ERP5Site with sql catalog_tool : In that case, we end up
              # running _bootstrap from here, leading to migration.
              # 2. New ERP5Site : In this case, we don't do anything here, cause
              # the catalog_tool would be ERP5CatalogTool, so this would just pass.
              continue
            tool = tool_class()
            portal._setObject(tool_id, tool, set_owner=False,
                              suppress_events=True)
            tool = getattr(portal, tool_id)
          elif tool._isBootstrapRequired():
            migrate = True
          else:
            continue
          tool._bootstrap()
          tool.__class__ = getattr(erp5.portal_type, tool.portal_type)
        # TODO: Create portal_activities here, and even before portal_types:
        #       - all code in ActiveObject could assume that it always exists
        #       - currently, some objects created very early are not indexed
        #         and this would fix this issue
        try:
          portal.portal_activities.initialize()
        except AttributeError:
          pass # no Activity Tool yet

        if migrate:
          portal.migrateToPortalTypeClass()
          portal.portal_skins.changeSkin(None)
          TransactionalResource(tpc_finish=lambda txn:
              _bootstrapped.add(portal.id))
          LOG('ERP5Site', INFO, 'Transition successful, please update your'
              ' business templates')
        else:
          _bootstrapped.add(portal.id)
      except:
        # Required because the exception may be silently dropped by the caller.
        transaction.doom()
        LOG('ERP5Site', PANIC, "Automatic migration of core tools failed",
            error=True)
        raise

    LOG("ERP5Type.dynamic", 0, "Resetting dynamic classes")
    try:
      for class_name, klass in inspect.getmembers(erp5.portal_type,
                                                  inspect.isclass):
        # Zope Interface is implemented through __implements__,
        # __implemented__ (both implementedBy instances) and __provides__
        # (ClassProvides instance) attributes set on the class by
        # zope.interface.declarations.implementedByFallback.
        #
        # However both implementedBy and ClassProvides instances keep a
        # reference to the class itself, thus creating a circular references
        # preventing erp5.* classes to be GC even when not being actually used
        # anywhere anymore after a reset.
        for k in klass.mro():
          if k.__module__.startswith('erp5.'):
            for attr in ('__implements__', '__implemented__', '__provides__'):
              if k.__dict__.get(attr) is not None:
                delattr(k, attr)

        klass.restoreGhostState()

      # Clear accessor holders of ZODB Property Sheets and Portal Types
      erp5.accessor_holder.clear()
      erp5.accessor_holder.property_sheet.clear()

      for name in erp5.accessor_holder.portal_type.__dict__.keys():
        if name[0] != '_':
          delattr(erp5.accessor_holder.portal_type, name)

    except Exception:
      # Allow easier debugging when the code is wrong as this
      # exception is catched later and re-raised as a BadRequest
      import traceback; traceback.print_exc()
      raise

    # It's okay for classes to keep references to old methods - maybe.
    # but we absolutely positively need to clear the workflow chains
    # stored in WorkflowMethod objects: our generation of workflow
    # methods adds/registers/wraps existing methods, but does not
    # remove old chains. Do it now.
    resetRegisteredWorkflowMethod()

    # Some method generations are based on portal methods, and portal
    # methods cache results. So it is safer to invalidate the cache.
    cache_tool = getattr(portal, 'portal_caches', None)
    if cache_tool is not None:
      cache_tool.clearCache()

    # Clear Zope Component Registries (Zope Adapters/Utilities cache lookup)
    # because it contains references to reset dynamic classes (which prevents
    # them from being GC and may create inconsistencies when Interfaces have
    # been changed)
    import zope.component
    gsm = zope.component.getGlobalSiteManager()
    gsm.adapters.changed(gsm)
    gsm.utilities.changed(gsm)
