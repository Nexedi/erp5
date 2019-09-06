##############################################################################
#
# Copyright (c) 2010-2012 Nexedi SARL and Contributors. All Rights Reserved.
#                         Nicolas Dumazet <nicolas.dumazet@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from types import ModuleType
from . import aq_method_lock
import sys
import imp

class PackageType(ModuleType):
  """
  If a module has a __path__attribute, it will be treated as a package
  (PEP 302), this is required for Introspection (for example pylint)
  """
  __path__ = []

class RefManager(dict):
  """
  self[ComponentTool.last_sync] = (HTTP_REQUEST_WEAKSET,
                                   COMPONENT_MODULE_SET)
  """
  def add_request(self, request_obj):
    from Products.ERP5Type.Tool.ComponentTool import last_sync
    from weakref import WeakSet
    # dict.setdefault() atomic from 2.7.3
    self.setdefault(last_sync, (WeakSet(), set()))[0].add(request_obj)

  def add_module(self, module_obj):
    # Zope Ready to handle requests
    #
    # * R1:
    # -> last_sync=-1: HTTPRequest.__init__:
    #    request_module_dict: {-1: ([R1], [])}
    # ERP5Type.Tool.ComponentTool Resetting Components
    # -> last_sync=12: ComponentTool.reset:
    #    request_module_dict: {-1: ([R1], [])}
    # -> last_sync=12: C1.__load_module:
    #    request_module_dict: {-1: ([R1], [C1])}
    # => R1 finished and can be gc'ed.
    #
    # * R2 using C1:
    # -> last_sync=12:
    #    request_module_dict: {-1: ([], [C1])}
    #
    # => While R2 is running, a reset is performed and clear '-1'
    #    => C1 is gc'ed.
    from Products.ERP5Type.Globals import get_request
    self.add_request(get_request())

    for (_, module_obj_set) in self.itervalues():
      module_obj_set.add(module_obj)

  def gc(self):
    """
    Remove cache items with no Request Left.
    """
    for (current_last_sync,
         (request_obj_weakset, _)) in self.items():
      if not request_obj_weakset:
        del self[current_last_sync]

  def clear(self):
    """
    Completely clear the cache. Should never be called except to
    simulate new Requests in Unit Tests for example.
    """
    super(RefManager, self).clear()
  
class ComponentPackageType(PackageType):
  """
  Package for ZODB Component keeping reference to ZODB Component module.

  When the reference counter of a module reaches 0, its globals are
  all reset to None. So, if a thread performs a reset while another
  one executes codes using globals (such as modules imported at module
  level), the latter one must keep a reference around to avoid
  reaching a reference count to 0.

  Initially, this reference was kept in the Request object itself, but
  this does not work with the following use case:

    1. R1 loads M1 and keep a reference in R1.
    2. R2 imports M1.
       => Hit sys.modules and not going through Import Hooks.
          => No way to know that this module is being used by R2.
    3. R1 finishes and is destroyed.
       => M1 reference counter reaches 0 => globals set to None.
    4. R2 uses a global in M1.

  Thus create a cache per 'last_sync' and keep a module reference for
  *all* last_sync in case a module is imported by another earlier
  last_sync Request.

  OTOH, this means that ZODB Components module *must* be imported at
  the top level, otherwise a module being relied upon may have a
  different API after reset, thus it may fail...
  """
  def __init__(self, *args, **kwargs):
    super(ComponentPackageType, self).__init__(*args, **kwargs)
    self.ref_manager = RefManager()

class DynamicModule(ModuleType):
  """This module may generate new objects at runtime."""
  # it's useful to have such a generic utility
  # please subclass it if you need ERP5-specific behaviors

  __file__ = __file__

  def __init__(self, name, factory, doc=None):
    super(DynamicModule, self).__init__(name, doc=doc)
    self._factory = factory

  def __getattr__(self, name):
    if name[:2] == '__':
      raise AttributeError('%r module has no attribute %r'
                           % (self.__name__, name))

    with aq_method_lock:
      try:
        return super(DynamicModule, self).__getattribute__(name)
      except AttributeError:
        obj = self._factory(name)
        # _factory can return an instance, a constant, or a class
        if isinstance(obj, type):
          # if it's a class we want to set __module__
          obj.__module__ = self.__name__
        elif isinstance(obj, ModuleType):
          # if it's a module we want to set the name according to the
          # module it's being added to
          obj.__name__ = "%s.%s" % (self.__name__, name)
        setattr(self, name, obj)
        return obj

def registerDynamicModule(name, factory):
  d = DynamicModule(name, factory)
  sys.modules[name] = d
  return d

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
      holds accessor holders common to ZODB Property Sheets and Portal Types
    erp5.accessor_holder.property_sheet
      holds accessor holders of ZODB Property Sheets
    erp5.accessor_holder.portal_type
      holds accessors holders of Portal Types
    erp5.component:
      holds ZODB Component packages
    erp5.component.module:
      holds Module (eg any module not being one of the following and used to be found in Products.NAME on FS)
    erp5.component.document:
      holds Document modules previously found in bt5 in $INSTANCE_HOME/Document
    erp5.component.interface:
      holds Interface modules previously found in Products.NAME.interfaces
    erp5.component.mixin:
      holds Mixin modules previously found in Products.NAME.mixin
    erp5.component.Tool:
      holds Tool modules previously found in Products.NAME.Tool
    erp5.component.extension:
      holds Extension modules previously found in bt5 in
      $INSTANCE_HOME/Extensions
    erp5.component.test:
      holds Live Test modules previously found in bt5 in $INSTANCE_HOME/test
  """
  erp5 = PackageType("erp5")

  # Document classes without physical import path
  erp5.document = ModuleType("erp5.document")

  # Portal types as classes
  from accessor_holder import AccessorHolderType, AccessorHolderModuleType

  erp5.accessor_holder = AccessorHolderModuleType("erp5.accessor_holder")
  erp5.accessor_holder.__path__ = []

  erp5.accessor_holder.property_sheet = \
      AccessorHolderModuleType("erp5.accessor_holder.property_sheet")

  erp5.accessor_holder.portal_type = registerDynamicModule(
    'erp5.accessor_holder.portal_type',
    AccessorHolderModuleType)

  from lazy_class import generateLazyPortalTypeClass
  erp5.portal_type = registerDynamicModule('erp5.portal_type',
                                           generateLazyPortalTypeClass)

  from portal_type_class import loadTempPortalTypeClass
  erp5.temp_portal_type = registerDynamicModule('erp5.temp_portal_type',
                                                loadTempPortalTypeClass)

  # ZODB Components
  erp5.component = ComponentPackageType("erp5.component")

  from component_package import (ComponentDynamicPackage,
                                 ToolComponentDynamicPackage)

  # Prevent other threads to create erp5.* packages and modules or seeing them
  # incompletely
  imp.acquire_lock()
  try:
    sys.modules["erp5"] = erp5
    sys.modules["erp5.document"] = erp5.document
    sys.modules["erp5.accessor_holder"] = erp5.accessor_holder
    sys.modules["erp5.accessor_holder.property_sheet"] = \
        erp5.accessor_holder.property_sheet
    sys.modules["erp5.component"] = erp5.component

    erp5.component.module = ComponentDynamicPackage('erp5.component.module',
                                                    'Module Component')

    erp5.component.extension = ComponentDynamicPackage('erp5.component.extension',
                                                       'Extension Component')

    erp5.component.document = ComponentDynamicPackage('erp5.component.document',
                                                      'Document Component')

    erp5.component.tool = ToolComponentDynamicPackage('erp5.component.tool',
                                                      'Tool Component')

    erp5.component.interface = ComponentDynamicPackage('erp5.component.interface',
                                                       'Interface Component')

    erp5.component.mixin = ComponentDynamicPackage('erp5.component.mixin',
                                                   'Mixin Component')

    erp5.component.test = ComponentDynamicPackage('erp5.component.test',
                                                  'Test Component')
  finally:
    imp.release_lock()
