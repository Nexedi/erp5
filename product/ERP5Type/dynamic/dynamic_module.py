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
import sys
import threading

class DynamicModule(ModuleType):
  """This module may generate new objects at runtime."""
  # it's useful to have such a generic utility
  # please subclass it if you need ERP5-specific behaviors

  __file__ = __file__

  def __init__(self, name, factory, doc=None):
    super(DynamicModule, self).__init__(name, doc=doc)
    self._factory = factory
    self._lock = threading.RLock()

  def __getattr__(self, name):
    if name[:2] == '__':
      raise AttributeError('%r module has no attribute %r'
                           % (self.__name__, name))
    with self._lock:
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
      holds component modules
    erp5.component.extension:
      holds extension classes previously found in bt5 in instancehome/Extensions
  """
  erp5 = ModuleType("erp5")
  sys.modules["erp5"] = erp5

  # Document classes without physical import path
  erp5.document = ModuleType("erp5.document")
  sys.modules["erp5.document"] = erp5.document

  # Portal types as classes
  from accessor_holder import AccessorHolderType, AccessorHolderModuleType

  erp5.accessor_holder = AccessorHolderModuleType("erp5.accessor_holder")
  sys.modules["erp5.accessor_holder"] = erp5.accessor_holder

  erp5.accessor_holder.property_sheet = \
      AccessorHolderModuleType("erp5.accessor_holder.property_sheet")

  sys.modules["erp5.accessor_holder.property_sheet"] = \
      erp5.accessor_holder.property_sheet

  erp5.accessor_holder.portal_type = registerDynamicModule(
    'erp5.accessor_holder.portal_type',
    AccessorHolderModuleType)

  from lazy_class import generateLazyPortalTypeClass
  erp5.portal_type = registerDynamicModule('erp5.portal_type',
                                           generateLazyPortalTypeClass)

  from portal_type_class import loadTempPortalTypeClass
  erp5.temp_portal_type = registerDynamicModule('erp5.temp_portal_type',
                                                loadTempPortalTypeClass)

  # Components
  from component_class import ComponentModule, generateComponentClassWrapper

  erp5.component = ComponentModule("erp5.component")
  sys.modules["erp5.component"] = erp5.component

  erp5.component.extension = registerDynamicModule(
    'erp5.component.extension',
    generateComponentClassWrapper('erp5.component.extension'))
