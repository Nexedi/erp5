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

import sys
import inspect
from types import ModuleType

from dynamic_module import registerDynamicModule

from Products.ERP5Type.Base import _aq_reset, Base
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Utils import setDefaultClassProperties
from Products.ERP5Type import document_class_registry, mixin_class_registry

from zope.interface import classImplements
from zLOG import LOG, ERROR, INFO, WARNING

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
    raise ImportError('Could not import document class %s' % classpath)

def _fillAccessorHolderList(accessor_holder_list,
                            create_accessor_holder_func,
                            property_sheet_name_set,
                            accessor_holder_module,
                            property_sheet_module):
  """
  Fill the accessor holder list with the given Property Sheets (which
  could be coming either from the filesystem or ZODB)
  """
  for property_sheet_name in property_sheet_name_set:
    # LOG("ERP5Type.dynamic", INFO,
    #     "Getting accessor holder for " + property_sheet_name)

    try:
      # Get the already generated accessor holder
      accessor_holder_list.append(getattr(accessor_holder_module,
                                          property_sheet_name))

    except AttributeError:
      # Generate the accessor holder as it has not been done yet
      try:
        accessor_holder_class = \
          create_accessor_holder_func(getattr(property_sheet_module,
                                              property_sheet_name))

      except AttributeError:
        LOG("ERP5Type.dynamic", ERROR,
            "Ignoring missing Property Sheet " + property_sheet_name)

        raise

      accessor_holder_list.append(accessor_holder_class)

      setattr(accessor_holder_module, property_sheet_name,
              accessor_holder_class)

    #   LOG("ERP5Type.dynamic", INFO,
    #       "Created accessor holder for %s in %s" % (property_sheet_name,
    #                                                 accessor_holder_module))

    # LOG("ERP5Type.dynamic", INFO,
    #     "Got accessor holder for " + property_sheet_name)

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
  'Types Tool':   {'type_class': 'TypesTool',
                   'generating': False},
  'Solver Tool': {'type_class': 'SolverTool',
                  'generating': False}
  }

def generatePortalTypeClass(portal_type_name):
  """
  Given a portal type, look up in Types Tool the corresponding
  Base Type object holding the definition of this portal type,
  and computes __bases__ and __dict__ for the class that will
  be created to represent this portal type
  """
  from Products.ERP5.ERP5Site import getSite
  site = getSite()

  # LOG("ERP5Type.dynamic", INFO, "Loading portal type " + portal_type_name)

  global core_portal_type_class_dict

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
      return ((klass,), [], {})

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

  if type_class is None:
    raise AttributeError('Document class is not defined on Portal Type %s' \
            % portal_type_name)

  type_class_path = document_class_registry.get(type_class)
  if type_class_path is None:
    raise AttributeError('Document class %s has not been registered:' \
                         ' cannot import it as base of Portal Type %s' \
                         % (type_class, portal_type_name))

  klass = _importClass(type_class_path)

  global property_sheet_generating_portal_type_set

  accessor_holder_list = []

  if portal_type_name not in property_sheet_generating_portal_type_set:
    # LOG("ERP5Type.dynamic", INFO,
    #     "Filling accessor holder list for portal_type " + portal_type_name)

    property_sheet_generating_portal_type_set.add(portal_type_name)

    property_sheet_tool = getattr(site, 'portal_property_sheets', None)

    property_sheet_set = set()

    # The Property Sheet Tool may be None if the code is updated but
    # the BT has not been upgraded yet with portal_property_sheets
    if property_sheet_tool is None:
      LOG("ERP5Type.dynamic", WARNING,
          "Property Sheet Tool was not found. Please update erp5_core "
          "Business Template")
    else:
      if portal_type is not None:
        # Get the Property Sheets defined on the portal_type and use the
        # ZODB Property Sheet rather than the filesystem only if it
        # exists in ZODB
        zodb_property_sheet_set = set(property_sheet_tool.objectIds())
        for property_sheet in portal_type.getTypePropertySheetList():
          if property_sheet in zodb_property_sheet_set:
            property_sheet_set.add(property_sheet)
      else:
        zodb_property_sheet_set = set()

      # Get the Property Sheets defined on the document and its bases
      # recursively. Fallback on the filesystem Property Sheet only and
      # only if the ZODB Property Sheet does not exist
      from Products.ERP5Type.Base import getClassPropertyList
      for property_sheet in getClassPropertyList(klass):
        # If the Property Sheet is a string, then this is a ZODB
        # Property Sheet
        #
        # NOTE: The Property Sheets of a document should be given as a
        #       string from now on
        if isinstance(property_sheet, basestring) and \
          property_sheet in zodb_property_sheet_set:
          property_sheet_name = property_sheet
          property_sheet_set.add(property_sheet_name)

    import erp5

    if property_sheet_set:
      # Initialize ZODB Property Sheets accessor holders
      _fillAccessorHolderList(
        accessor_holder_list,
        property_sheet_tool.createZodbPropertySheetAccessorHolder,
        property_sheet_set,
        erp5.accessor_holder,
        property_sheet_tool)

    property_sheet_generating_portal_type_set.remove(portal_type_name)

  # LOG("ERP5Type.dynamic", INFO,
  #     "Filled accessor holder list for portal_type %s (%s)" % \
  #     (portal_type_name, accessor_holder_list))

  mixin_path_list = []
  if mixin_list:
    mixin_path_list = map(mixin_class_registry.__getitem__, mixin_list)
  mixin_class_list = map(_importClass, mixin_path_list)

  base_class_list = [klass] + accessor_holder_list + mixin_class_list

  interface_class_list = []
  if interface_list:
    from Products.ERP5Type import interfaces
    interface_class_list = [getattr(interfaces, name)
                            for name in interface_list]

  if portal_type_name in core_portal_type_class_dict:
    core_portal_type_class_dict[portal_type_name]['generating'] = False

  #LOG("ERP5Type.dynamic", INFO,
  #    "Portal type %s loaded with bases %s" \
  #        % (portal_type_name, repr(baseclasses)))

  return (tuple(base_class_list),
          interface_class_list,
          dict(portal_type=portal_type_name))

from lazy_class import generateLazyPortalTypeClass
def initializeDynamicModules():
  """
  Create erp5 module and its submodules
    erp5.portal_type
      holds portal type classes
    erp5.temp_portal_type
      holds portal type classes for temp objects
    erp5.document
      holds document classes that have no physical import path,
      for example classes created through ClassTool that are in
      $INSTANCE_HOME/Document
    erp5.accessor_holder
      holds accessors of ZODB Property Sheets
  """
  erp5 = ModuleType("erp5")
  sys.modules["erp5"] = erp5
  erp5.document = ModuleType("erp5.document")
  sys.modules["erp5.document"] = erp5.document
  erp5.accessor_holder = ModuleType("erp5.accessor_holder")
  sys.modules["erp5.accessor_holder"] = erp5.accessor_holder

  portal_type_container = registerDynamicModule('erp5.portal_type',
                                                generateLazyPortalTypeClass)

  erp5.portal_type = portal_type_container

  def loadTempPortalTypeClass(portal_type_name):
    """
    Returns a class suitable for a temporary portal type

    This class will in fact be a subclass of erp5.portal_type.xxx, which
    means that loading an attribute on this temporary portal type loads
    the lazily-loaded parent class, and that any changes on the parent
    class will be reflected on the temporary objects.
    """
    klass = getattr(portal_type_container, portal_type_name)

    from Products.ERP5Type.Accessor.Constant import PropertyGetter as \
      PropertyConstantGetter

    class TempDocument(klass):
      isTempDocument = PropertyConstantGetter('isTempDocument', value=True)
      __roles__ = None
    TempDocument.__name__ = "Temp " + portal_type_name

    # Replace some attributes.
    for name in ('isIndexable', 'reindexObject', 'recursiveReindexObject',
                 'activate', 'setUid', 'setTitle', 'getTitle', 'getUid'):
      setattr(TempDocument, name, getattr(klass, '_temp_%s' % name))

    # Make some methods public.
    for method_id in ('reindexObject', 'recursiveReindexObject',
                      'activate', 'setUid', 'setTitle', 'getTitle',
                      'edit', 'setProperty', 'getUid', 'setCriterion',
                      'setCriterionPropertyList'):
      setattr(TempDocument, '%s__roles__' % method_id, None)
    return TempDocument

  erp5.temp_portal_type = registerDynamicModule('erp5.temp_portal_type',
                                                loadTempPortalTypeClass)

last_sync = 0
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

  LOG("ERP5Type.dynamic", 0, "Resetting dynamic classes")

  import erp5

  Base.aq_method_lock.acquire()
  try:
    for class_name, klass in inspect.getmembers(erp5.portal_type,
                                                inspect.isclass):
      klass.restoreGhostState()
  finally:
    Base.aq_method_lock.release()

  # Clear accessor holders of ZODB Property Sheets
  for property_sheet_id in erp5.accessor_holder.__dict__.keys():
    if not property_sheet_id.startswith('__'):
      delattr(erp5.accessor_holder, property_sheet_id)

  # Necessary because accessors are wrapped in WorkflowMethod by
  # _aq_dynamic (performed in createAccessorHolder)
  _aq_reset()
