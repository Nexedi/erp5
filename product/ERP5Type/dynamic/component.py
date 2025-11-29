# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2025 Nexedi SARL and Contributors. All Rights Reserved.
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
##############################################################################

import sys
import os
import errno
import coverage
import traceback

from types import ModuleType
from importlib import import_module
from zLOG import LOG, BLATHER, WARNING
from Products.ERP5Type.patches.Restricted import MNAME_MAP

from AccessControl.SecurityInfo import _moduleSecurity, _appliedModuleSecurity
from Products.ERP5Type.Utils import ensure_list

class ComponentImportError(ImportError):
  """Error when importing an existing, but invalid component, typically
  because it contains syntax errors or import errors.
  """
  # TODO: needed?

from importlib.abc import MetaPathFinder, Loader, InspectLoader
from importlib.machinery import ModuleSpec
from Products.ERP5.ERP5Site import getSite
from Acquisition import aq_base

class ComponentModuleLoader(InspectLoader):
  fullname_source_code_dict = {}

  def create_module(self, spec):
    # __name__, __loader__, __package__, __spec__, __path__, __file__ (origin)
    # and __cached__ set by importlib._bootstrap._init_module_attrs()
    return ModuleType(spec.name, spec.component_description)

  def exec_module(self, module):
    spec = module.__spec__
    component = getattr(getSite().portal_components, spec.component_id)
    source_code = spec.component_source_code

    self.fullname_source_code_dict[spec.name] = source_code
    try:
      code_obj = compile(source_code, module.__file__, 'exec')
      exec(code_obj, module.__dict__)
    except Exception:
      from six import reraise
      # TODO: Do we need ComponentImportError?
      reraise(
        ComponentImportError,
        ComponentImportError("Cannot load Component %s:\n%s" % (
          spec.name, traceback.format_exc())),
        sys.exc_info()[2])

    component._hookAfterLoad(module)

    import erp5.component
    erp5.component.ref_manager.add_module(module)

    LOG("ERP5Type.dynamic.component", WARNING,
        "=====> ComponentModuleLoader: %r" % (module))

    return module

  @classmethod
  def get_source(cls, fullname):
    """
    PEP-302 function to get the source code, used mainly by linecache for
    tracebacks, pdb...

    Use internal cache rather than accessing the Component directly as this
    would require accessing ERP5 Site even though the source code may be
    retrieved outside of ERP5 (eg DeadlockDebugguer).
    """
    return cls.fullname_source_code_dict.get(fullname)
COMPONENT_MODULE_LOADER_INSTANCE = ComponentModuleLoader()

class ComponentAliasLoader(Loader):
  def create_module(self, _):
    pass

  def exec_module(self, module):
    spec = module.__spec__

    # TODO: Check that the alias module is deleted in case of Exception
    real_module = import_module(spec.real_name)
    sys.modules[spec.name] = real_module
    MNAME_MAP[spec.name] = spec.real_name

    LOG("ERP5Type.dynamic.component", WARNING,
        "=====> ComponentAliasLoader: %s ALIAS TO %s" % (spec.real_name,
                                                         spec.name))
COMPONENT_ALIAS_LOADER_INSTANCE = ComponentAliasLoader()

class ComponentDynamicPackage(ModuleType):
  __path__ = []

  # TODO: Review use cases
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
      return import_module(fullname)
    except ImportError:
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
      # Clear the source code dict only once
      ComponentModuleLoader.fullname_source_code_dict.clear()
      package = self

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
      elif name.endswith('_version'): # TODO: isinstance(module, ComponentVersionPackage):
        self.reset(sub_package=module)

      module_name = package.__name__ + '.' + name
      LOG("ERP5Type.Tool.ComponentTool", BLATHER, "Resetting " + module_name)

      # The module must be deleted first from sys.modules to avoid imports in
      # the meantime
      del sys.modules[module_name]

      delattr(package, name)

class ToolComponentDynamicPackage(ComponentDynamicPackage):
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

    super(ToolComponentDynamicPackage, self).reset(*args, **kw)

_VERSION_SUFFIX_LEN = len('_version')
COMPONENT_PACKAGE_NAME_CLASS_DICT = {
  'module': ComponentDynamicPackage,
  'extension': ComponentDynamicPackage,
  'document': ComponentDynamicPackage,
  'interface': ComponentDynamicPackage,
  'mixin': ComponentDynamicPackage,
  'test': ComponentDynamicPackage,
  'tool': ToolComponentDynamicPackage,
}

class ComponentMetaPathFinder(MetaPathFinder):
  def find_spec(self, fullname, path, target=None):
    try:
      site = getSite()
    except IndexError:
      # We cannot do anything until ERP5Site is created and ready...
      return None

    # fullname=erp5.component.PACKAGE.*: ZODB Components
    if not path:
      if not fullname.startswith('erp5.component.'):
        return None
    # fullname=Products.PACKAGE.*: Filesystem import backward-compatibility
    else:
      # TODO: Should we filter by `path`?
      import erp5.component
      if erp5.component.filesystem_import_dict is None:
        erp5.component.createFilesystemImportDict()
      try:
        real_name = erp5.component.filesystem_import_dict[fullname]
      except KeyError:
        return None
      else:
        spec = ModuleSpec(fullname, loader=COMPONENT_ALIAS_LOADER_INSTANCE)
        spec.real_name = real_name
        return spec

    package_name = fullname.split('.', 3)[2]
    if package_name not in COMPONENT_PACKAGE_NAME_CLASS_DICT:
      return None

    spec = None
    name = fullname[len('erp5.component.' + package_name + '.'):]
    # name=VERSION_version.REFERENCE
    if '.' in name:
      try:
        version, name = name.split('.')
        version = version[:-_VERSION_SUFFIX_LEN]
      except ValueError:
        return None

      id_ = "%s.%s.%s" % (package_name, version, name)
      # aq_base() because this should not go up to ERP5Site and trigger
      # side-effects, after all this only check for existence...
      component = getattr(aq_base(site.portal_components), id_, None)
      if component is None or component.getValidationState() not in (
          'modified', 'validated'):
        # TODO
        if component is None:
          message = "'%s' does not exist" % id_
        else:
          message = "Not in modified/validated state ('%s')" % component.getValidationState()
        message = "Could not load Component module '%r': %s" % (fullname, message)
        raise ModuleNotFoundError(message)

      # TODO: Unit Test?
      for override_path in os.environ.get('ERP5_COMPONENT_OVERRIDE_PATH',
                                          '').split(os.pathsep):
        filepath = os.path.join(override_path, id_ + '.py')
        if os.path.isfile(filepath) and os.access(filepath, os.R_OK):
          LOG("component", WARNING, "Using local override %s" % filepath)
          return ModuleSpec(fullname, loader=SourceFileLoader(fullname, filepath))

      origin = 'erp5://portal_components/' + id_
      # TODO: cost?
      if coverage.Coverage.current():
        try:
          origin = component._erp5_coverage_filename
        except AttributeError:
          LOG("ERP5Type.Tool.ComponentTool", WARNING,
              "No coverage filesystem mapping for %s" % fullname)

      spec = ModuleSpec(fullname,
                        loader=COMPONENT_MODULE_LOADER_INSTANCE,
                        origin=origin)
      spec.has_location = True # __file__ set to `origin`
      spec.component_id = id_
      spec.component_description = component.getDescription()
      spec.component_source_code = component.getTextContent(validated_only=True)

    # name=VERSION_version => package
    elif name.endswith('_version'):
      if name[:-_VERSION_SUFFIX_LEN] in site.getVersionPriorityNameList():
        spec = ModuleSpec(fullname, loader=None, is_package=True)
      else:
        # TODO
        message = (
          "Could not load Component module '%r': '%s' not in "
          "version_priority_name_list=%r" % (fullname,
                                             name[:-_VERSION_SUFFIX_LEN],
                                             site.getVersionPriorityNameList()))
        raise ModuleNotFoundError(message)

    # name=REFERENCE (alias to HIGHEST_VERSION_AVAILABLE_version.REFERENCE)
    else:
      # aq_base() because this should not go up to ERP5Site and trigger
      # side-effects, after all this only check for existence...
      component_tool = aq_base(site.portal_components)
      for version in site.getVersionPriorityNameList():
        id_ = "%s.%s.%s" % (package_name, version, name)
        component = getattr(component_tool, id_, None)
        if component is not None and component.getValidationState() in (
            'modified', 'validated'):
          real_name = "erp5.component.%s.%s_version.%s" % (package_name, version, name)
          spec = ModuleSpec(fullname, loader=COMPONENT_ALIAS_LOADER_INSTANCE)
          spec.real_name = real_name
          break
      else:
        # TODO
        message = (
          "Could not load Component module '%r': "
          "None found in modified/validated state (searched IDs=%r,version_priority_name_list=%r)" %
          (fullname,
           ["%s.%s.%s" % (package_name, version, name) for version in site.getVersionPriorityNameList()],
           site.getVersionPriorityNameList()))
        raise ModuleNotFoundError(message)

    return spec

def register_all_component_package():
  import erp5

  from .dynamic_module import ComponentPackageType # WIP: to be moved in this file?
  erp5.component = ComponentPackageType("erp5.component")
  sys.modules['erp5.component'] = erp5.component

  for package_name, package_class in COMPONENT_PACKAGE_NAME_CLASS_DICT.items():
    package_fullname = 'erp5.component.' + package_name
    package = package_class(package_fullname)

    setattr(erp5.component, package_name, package)
    sys.modules[package_fullname] = package

  sys.meta_path.append(ComponentMetaPathFinder())
