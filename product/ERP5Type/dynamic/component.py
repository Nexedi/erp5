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

from Products.ERP5Type.patches.Restricted import MNAME_MAP

class ComponentPackage(ModuleType):
  """
  TODO: Do we really need ComponentVersionPackage?
  """
  __path__ = []

from AccessControl.SecurityInfo import _moduleSecurity, _appliedModuleSecurity
# WIP
class ComponentDynamicPackage(ComponentPackage):
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
      self.__fullname_source_code_dict.clear()
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
      elif isinstance(module, ComponentVersionPackage):
        self.reset(sub_package=module)

      module_name = package.__name__ + '.' + name
      LOG("ERP5Type.Tool.ComponentTool", BLATHER, "Resetting " + module_name)

      # The module must be deleted first from sys.modules to avoid imports in
      # the meantime
      del sys.modules[module_name]

      delattr(package, name)

# WIP
class ToolComponentDynamicPackage(ComponentDynamicPackage):
  def reset(self, *args, **kw):
    """
    Reset CMFCore list of Tools (manage_addToolForm)
    """
    import Products.ERP5
    toolinit = Products.ERP5.__FactoryDispatcher__.toolinit
    reset_tool_set = set()
    for tool in toolinit.tools:
      if not tool.__module__.startswith(self._namespace_prefix):
        reset_tool_set.add(tool)
    toolinit.tools = reset_tool_set

    super(ToolComponentDynamicPackage, self).reset(*args, **kw)

COMPONENT_PACKAGE_NAMESPACE_CLASS_DICT = {
  'erp5.component.module': ComponentDynamicPackage,
  'erp5.component.extension': ComponentDynamicPackage,
  'erp5.component.document': ComponentDynamicPackage,
  'erp5.component.interface': ComponentDynamicPackage,
  'erp5.component.mixin' ComponentDynamicPackage,
  'erp5.component.test': ComponentDynamicPackage,
  'erp5.component.tool': ToolComponentDynamicPackage,
}

_VERSION_SUFFIX_LEN = len('_version')

from importlib.abc import MetaPathFinder, InspectLoader
from importlib.machinery import ModuleSpec
from Products.ERP5.ERP5Site import getSite
from Acquisition import aq_base

from types import ModuleType

class ComponentModuleLoader(InspectLoader):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fullname_source_code_dict = {}

  def create_module(self, spec):
    return ModuleType(spec.name, component.getDescription())

  def get_source(self, fullname):
    """
    PEP-302 function to get the source code, used mainly by linecache for
    tracebacks, pdb...

    Use internal cache rather than accessing the Component directly as this
    would require accessing ERP5 Site even though the source code may be
    retrieved outside of ERP5 (eg DeadlockDebugguer).
    """
    return self.fullname_source_code_dict.get(fullname)

  def exec_module(self, module):
    pass

class ComponentAliasLoader(InspectLoader):
  def create_module(self, spec):
    pass

  def get_source(self, fullname):
    pass

  def exec_module(self, module):
    pass

class ComponentMetaPathFinder(MetaPathFinder):
  def find_spec(self, fullname, path, target=None):
    if path:
      # Filesystem-based import backward-compatibility
      import erp5.component
      try:
        fullname = erp5.component.filesystem_import_dict.get(fullname, '')
      except AttributeError: # filesystem_import_dict may not exist yet during bootstrap
        return None

    namespace = fullname.rsplit('.', 3)
    if namespace not in COMPONENT_PACKAGE_NAMESPACE_CLASS_DICT:
      return None

    site = getSite()
    id_prefix = namespace.rsplit('.', 1)[1]
    name = fullname[len(namespace + '.'):]

    # name=VERSION_version.REFERENCE
    if '.' in name:
      try:
        version, name = name.split('.')
        version = version[:-__VERSION_SUFFIX_LEN]
      except ValueError:
        return None

      id_ = "%s.%s.%s" % (id_prefix, version, name)
      # aq_base() because this should not go up to ERP5Site and trigger
      # side-effects, after all this only check for existence...
      component = getattr(aq_base(site.portal_components), id_, None)
      if component is not None and component.getValidationState() in ('modified',
                                                                      'validated'):
        spec = ModuleSpec(fullname, loader=ComponentModuleLoader)
        spec.component_id = id_

    # Skip unavailable components, otherwise Products for example could be
    # wrongly considered as importable and thus the actual filesystem class
    # ignored
    #
    # name=VERSION_version => this is a package
    elif name.endswith('_version'):
      if name[:-__VERSION_SUFFIX_LEN] in site.getVersionPriorityNameList():
        return ModuleSpec(fullname, loader=None, is_package=True)

    # name=REFERENCE
    else:
      component_tool = aq_base(site.portal_components)
      for version in site.getVersionPriorityNameList():
        id_ = "%s.%s.%s" % (id_prefix, version, name)
        component = getattr(component_tool, id_, None)
        if component is not None and component.getValidationState() in ('modified',
                                                                        'validated'):
          return ModuleSpec(fullname, loader=ComponentAliasLoader)

    return None
