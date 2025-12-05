# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012-2025 Nexedi SARL and Contributors. All Rights Reserved.
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

import errno
import os
import six
import sys
import collections
from six import reraise
import traceback

import coverage
from Products.ERP5Type.Utils import ensure_list
from Products.ERP5.ERP5Site import getSite
from Products.ERP5Type import product_path as ERP5Type_product_path
from . import aq_method_lock, global_import_lock
from .dynamic_module import PackageType
from types import ModuleType
from zLOG import LOG, BLATHER, WARNING
from Acquisition import aq_base
from importlib import import_module
from Products.ERP5Type.patches.Restricted import MNAME_MAP
from AccessControl.SecurityInfo import _moduleSecurity, _appliedModuleSecurity

COMPONENT_PACKAGE_NAME_SET = {
  'module',
  'extension',
  'document',
  'interface',
  'mixin',
  'test',
  'tool',
}

class ComponentVersionPackageType(PackageType):
  """
  Component Version package (erp5.component.PACKAGE.VERSION_version)
  """

class ComponentImportError(ImportError):
  """Error when importing an existing, but invalid component, typically 
  because it contains syntax errors or import errors.
  """

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

    for (_, module_obj_set) in six.itervalues(self):
      module_obj_set.add(module_obj)

  def gc(self):
    """
    Remove cache items with no Request Left.
    """
    from Products.ERP5Type.Utils import ensure_list
    for (current_last_sync,
         (request_obj_weakset, _)) in ensure_list(self.items()):
      if not request_obj_weakset:
        del self[current_last_sync]

  def clear(self):
    """
    Completely clear the cache. Should never be called except to
    simulate new Requests in Unit Tests for example.
    """
    super(RefManager, self).clear()

class ERP5ComponentPackageType(PackageType):
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
  # 'Products.ERP5.Document.Person' => 'erp5.component.document.Person'
  filesystem_import_dict = None

  def __init__(self):
    super(ERP5ComponentPackageType, self).__init__('erp5.component',
                                                   'ERP5 Component top-level Package')
    self.ref_manager = RefManager()

  def createFilesystemImportDict(self):
    """
    Make legacy filesystem classes importable even after their migration to
    ZODB Components
    """
    from Products.ERP5.ERP5Site import getSite
    from Acquisition import aq_base
    site = getSite()
    try:
      component_tool = aq_base(site.portal_components)
    except AttributeError:
      # For old sites without portal_components, just use FS Documents...
      raise
    filesystem_import_dict = {}
    for component in component_tool.objectValues():
      if component.getValidationState() == 'validated':
        component_module_name = '%s.%s' % (component._getDynamicModuleNamespace(),
                                           component.getReference())
        if component.getSourceReference() is not None:
          # Add an alias that with import name before migration to ZODB Components (MR !1271)
          filesystem_import_dict[component.getSourceReference()] = component_module_name

        if component.getPortalType() == 'Document Component':
          # For old instances of Document classes having as their __class__
          # Products.ERP5Type.Document.DOCUMENT.CLASS (MR !1240)
          filesystem_import_dict[('Products.ERP5Type.Document.' +
                                  component.getReference())] = component_module_name

    self.filesystem_import_dict = filesystem_import_dict

class ComponentDynamicPackageType(PackageType):
  """
  A top-level component is a package as it contains modules, this is required
  to be able to add import hooks (as described in PEP 302) when a in the
  source code of a Component, another Component is imported.

  A Component is loaded when being imported, for example in a Document
  Component with ``import erp5.component.XXX.YYY'', through the Importer
  Protocol (PEP 302), by adding an instance of this class to sys.meta_path and
  through find_module() and load_module() methods. The latter method takes
  care of loading the code into a new module.

  This is required because Component classes do not have any physical location
  on the filesystem, however extra care must be taken for performances because
  load_module() will be called each time an import is done, therefore the
  loader should be added to sys.meta_path as late as possible to keep startup
  time to the minimum.
  """
  def find_load_module(self, name):
    """
    Find and load a Component module.

    When FS fallback is required (mainly for Document and Extension), this
    should be used over a plain import to distinguish a document not available
    as ZODB Component to an error in a Component, especially because in the
    latter case only ImportError can be raised (PEP-302).

    For example: if a Component tries to import another Component module but
    the latter has been disabled and there is a fallback on the filesystem, a
    plain import would hide the real error, instead log it...
    """
    fullname = self.__name__ + '.' + name
    try:
      # Wrapper around __import__ much faster than calling find_module() then
      # load_module(), and returning module 'name' in contrary to __import__
      # returning 'erp5' (requiring fromlist parameter which is slower)
      return import_module(fullname)
    except ModuleNotFoundError:
      pass
    except ImportError as e:
      LOG("ERP5Type.dynamic", WARNING,
          "Could not load Component module %r" % fullname, error=True)

    return None

  def reset(self, sub_package=None):
    """
    Reset the content of the current package and its version package as well
    recursively. This method must be called within a lock to avoid side
    effects
    """
    if sub_package:
      package = sub_package
    else:
      package = self
      # Clear the source code dict only once
## TODO      
####      package.__loader__.fullname_source_code_dict.clear()

      # Force reload of ModuleSecurityInfo() as it may have been changed in
      # the source code
      for modsec_dict in _moduleSecurity, _appliedModuleSecurity:
        for k in ensure_list(modsec_dict.keys()):
          if k.startswith(self.__name__):
            del modsec_dict[k]
      for k, v in ensure_list(MNAME_MAP.items()):
        if v.startswith(self.__name__):
          del MNAME_MAP[k]

          # Products import compatibility (module_fullname_filesystem)
          if k.startswith('Products.'):
            del sys.modules[k]

    for name, module in ensure_list(package.__dict__.items()):
      if name[0] == '_' or not isinstance(module, ModuleType):
        continue

      # Reset the content of the version package before resetting it
      elif isinstance(module, ComponentVersionPackageType):
        self.reset(sub_package=module)

      module_name = package.__name__ + '.' + name
      LOG("ERP5Type.Tool.ComponentTool", BLATHER, "Resetting " + module_name)

      # The module must be deleted first from sys.modules to avoid imports in
      # the meantime
      del sys.modules[module_name]

      delattr(package, name)

class ToolComponentDynamicPackageType(ComponentDynamicPackageType):
  def reset(self, *args, **kw):
    """
    Reset CMFCore list of Tools (manage_addToolForm)
    """
    import Products.ERP5
    toolinit = Products.ERP5.__FactoryDispatcher__.toolinit
    reset_tool_set = set()
    for tool in toolinit.tools:
      if not tool.__module__.startswith(self.__name__):
        reset_tool_set.add(tool)
    toolinit.tools = reset_tool_set

    super(ToolComponentDynamicPackageType, self).reset(*args, **kw)
