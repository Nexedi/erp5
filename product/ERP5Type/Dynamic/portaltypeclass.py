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

import dynamicmodule
import lazyclass

from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Utils import setDefaultClassProperties
from Products.ERP5Type import document_class_registry, mixin_class_registry
from Products.ERP5Type import PropertySheet as FilesystemPropertySheet
from ExtensionClass import Base as ExtensionBase
from zLOG import LOG, ERROR, INFO

def _import_class(classpath):
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

def _create_accessor_holder_class(property_sheet_tool,
                                  property_sheet_module,
                                  property_sheet_name):
  """
  If the given Property Sheet exists in portal_property_sheets, then
  generate its accessor holder
  """

def _fill_accessor_holder_list(accessor_holder_list,
                               create_accessor_holder_func,
                               property_sheet_name_set,
                               accessor_holder_module,
                               property_sheet_module):
  """
  Fill the accessor holder list with the given Property Sheets (which
  could be coming either from the filesystem or ZODB)
  """
  for property_sheet_name in property_sheet_name_set:
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
        # Not too critical
        LOG("ERP5Type.Dynamic", ERROR,
            "Ignoring missing Property Sheet " + property_sheet_name)

      else:
        setattr(accessor_holder_module, property_sheet_name,
                accessor_holder_class)

        accessor_holder_list.append(accessor_holder_class)

        LOG("ERP5Type.Dynamic", INFO,
            "Created accessor holder for %s in %s" % (property_sheet_name,
                                                      accessor_holder_module))

def portal_type_factory(portal_type_name):
  """
  Given a portal type, look up in Types Tool the corresponding
  Base Type object holding the definition of this portal type,
  and computes __bases__ and __dict__ for the class that will
  be created to represent this portal type
  """
  #LOG("ERP5Type.Dynamic", 0, "Loading portal type %s..." % portal_type_name)

  type_class = None
  mixin_list = []
  interface_list = []
  accessor_holder_list = []

  from Products.ERP5.ERP5Site import getSite
  site = getSite()

  type_tool = site.portal_types
  try:
    portal_type = getattr(type_tool, portal_type_name)
  except:
    raise AttributeError('portal type %s not found in Types Tool' \
                            % portal_type_name)

  # type_class has a compatibility getter that should return
  # something even if the field is not set (i.e. Base Type object
  # was not migrated yet)
  try:
    type_class = portal_type.getTypeClass()

    # But no such getter exists for Mixins and Interfaces:
    # in reality, we can live with such a failure
    try:
      mixin_list = portal_type.getTypeMixinList()
      interface_list = portal_type.getTypeInterfaceList()
    except StandardError:
      # log loudly the error, but it's not _critical_
      LOG("ERP5Type.Dynamic", ERROR,
          "Could not load interfaces or Mixins for portal type %s" \
              % portal_type_name)
  except AttributeError:
    # Try to figure out a coresponding document class from the document side.
    # This is required for the bootstrap (e.g. Base Type).
    for name, path in document_class_registry.iteritems():
      # XXX heuristic: bootstrap issues should happen only inside ERP5Type.
      if not path.startswith('Products.ERP5Type.'):
        continue

      module_path, class_name = path.rsplit('.', 1)
      module = __import__(module_path, {}, {}, (module_path,))
      klass = getattr(module, class_name)
      try:
        try:
          document_portal_type = getattr(klass, 'portal_type')
          if document_portal_type == portal_type_name:
            type_class = name
            break
        except AttributeError:
          pass
      finally:
        del klass

  import erp5

#broken#    # Initialize filesystem Property Sheets accessor holders
#broken#    _fill_accessor_holder_list(
#broken#      accessor_holder_list,
#broken#      site.portal_property_sheets.createFilesystemPropertySheetAccessorHolder,
#broken#      set(portal_type.getTypePropertySheetList() or ()),
#broken#      erp5.filesystem_accessor_holder,
#broken#      FilesystemPropertySheet)
#broken#
#broken#    # Initialize ZODB Property Sheets accessor holders
#broken#    _fill_accessor_holder_list(
#broken#      accessor_holder_list,
#broken#      site.portal_property_sheets.createZodbPropertySheetAccessorHolder,
#broken#      set(portal_type.getTypeZodbPropertySheetList() or ()),
#broken#      erp5.zodb_accessor_holder,
#broken#      site.portal_property_sheets)

    #LOG("ERP5Type.Dynamic", INFO,
    #    "%s: accessor_holder_list: %s" % (portal_type_name,
    #                                      accessor_holder_list))

  if type_class is not None:
    type_class = document_class_registry.get(type_class)
  if type_class is None:
    raise AttributeError('Document class is not defined on Portal Type %s' % portal_type_name)

  type_class = _import_class(type_class)

  mixin_path_list = []
  if mixin_list:
    mixin_path_list = map(mixin_class_registry.__getitem__, mixin_list)
  mixin_class_list = map(_import_class, mixin_path_list)

  baseclasses = [type_class] + accessor_holder_list + mixin_class_list

  #LOG("ERP5Type.Dynamic", INFO,
  #    "Portal type %s loaded with bases %s" \
  #        % (portal_type_name, repr(baseclasses)))

  return tuple(baseclasses), dict(portal_type=portal_type_name)

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
    erp5.zodb_accessor_holder
      holds accessors of ZODB Property Sheets
    erp5.filesystem_accessor_holder
      holds accessors of filesystem Property Sheets

  XXX: there should be only one accessor_holder once the code is
       stable and all the Property Sheets have been migrated
  """
  def portal_type_loader(portal_type_name):
    """
    Returns a lazily-loaded "portal-type as a class"
    """
    return lazyclass.lazyclass(portal_type_name, portal_type_factory)

  erp5 = ModuleType("erp5")
  sys.modules["erp5"] = erp5
  erp5.document = ModuleType("erp5.document")
  sys.modules["erp5.document"] = erp5.document

  erp5.zodb_accessor_holder = ModuleType("erp5.zodb_accessor_holder")
  sys.modules["erp5.zodb_accessor_holder"] = erp5.zodb_accessor_holder
  erp5.filesystem_accessor_holder = ModuleType("erp5.filesystem_accessor_holder")
  sys.modules["erp5.filesystem_accessor_holder"] = erp5.filesystem_accessor_holder

  portal_type_container = dynamicmodule.dynamicmodule('erp5.portal_type',
                                                      portal_type_loader)

  erp5.portal_type = portal_type_container

  def temp_portal_type_loader(portal_type_name):
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
    TempDocument.__name__ = "Temp" + portal_type_name

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

  erp5.temp_portal_type = dynamicmodule.dynamicmodule('erp5.temp_portal_type',
                                                   temp_portal_type_loader)

def _clear_accessor_holder_module(module):
  """
  Clear the given accessor holder module (either for filesystem or
  ZODB)

  XXX: Merge into synchronizeDynamicModules as soon as we get rid of
       these two accessor holder modules
  """
  for property_sheet_id in module.__dict__.keys():
    if not property_sheet_id.startswith('__'):
      delattr(module, property_sheet_id)

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

  LOG("ERP5Type.Dynamic", 0, "Resetting dynamic classes")

  import erp5

  for class_name, klass in inspect.getmembers(erp5.portal_type,
                                              inspect.isclass):
    ghostbase = getattr(klass, '__ghostbase__', None)
    if ghostbase is not None:
      for attr in klass.__dict__.keys():
        if attr != '__module__':
          delattr(klass, attr)
      klass.__bases__ = ghostbase
      type(ExtensionBase).__init__(klass, klass)

  # Clear accessor holders of ZODB Property Sheets
  _clear_accessor_holder_module(erp5.zodb_accessor_holder)

  # Clear accessor holders of filesystem Property Sheets
  _clear_accessor_holder_module(erp5.filesystem_accessor_holder)
