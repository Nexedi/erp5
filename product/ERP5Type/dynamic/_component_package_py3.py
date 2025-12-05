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

import os
import sys
import coverage
import traceback

from zLOG import LOG, BLATHER, WARNING
from Acquisition import aq_base
from Products.ERP5.ERP5Site import getSite
from Products.ERP5Type.patches.Restricted import MNAME_MAP
from . import aq_method_lock

from importlib import import_module
from importlib.abc import MetaPathFinder, Loader, InspectLoader
from importlib.machinery import ModuleSpec, SourceFileLoader

from .component_package import (ComponentVersionPackageType,
                                COMPONENT_PACKAGE_NAME_SET,
                                ComponentImportError)

class ComponentVersionPackageLoader(Loader):
  def create_module(self, spec):
    if spec.component_version_package_name not in getSite().getVersionPriorityNameList():
      error_message = "%s: No such version" % spec.name
      LOG("ERP5Type.dynamic.component", BLATHER, error_message)
      raise ModuleNotFoundError(error_message)
    return ComponentVersionPackageType(spec.name)

  def exec_module(self, _):
    pass
COMPONENT_VERSION_PACKAGE_LOADER_INSTANCE = ComponentVersionPackageLoader()

class ComponentModuleLoader(InspectLoader):
  fullname_source_code_dict = {}
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

  def create_module(self, _):
    # __name__, __loader__, __package__, __spec__, __path__, __file__ (`origin`)
    # and __cached__ set by `importlib._bootstrap._init_module_attrs()` so let
    # importlib create a ModuleType()...
    pass

  # TODO: aq_method_lock was in load_module() before. Perhaps, it should be
  # acquired when module lock is acquired (`with _ModuleLockManager(name)`)?
  def exec_module(self, module):
    """As much as possible is already done in find_spec() and set on ModuleSpec
    object to avoid further computation here...

    TODO: Add such comment on find_spec()
    """
    spec = module.__spec__

    # aq_base() because this should not go up to ERP5Site and trigger
    # side-effects, after all this only check for existence...
    component = getattr(aq_base(getSite().portal_components),
                        spec.component_id, None)

    error_message = None
    if component is None:
      error_message = "%s: %s does not exist" % (spec.name, spec.component_id)
    elif component.getValidationState() not in ('modified', 'validated'):
      error_message = "%s: %s not modified/validated (state=%s)" % (
        spec.name, spec.component_id, component.getValidationState())
    if error_message is not None:
      LOG("ERP5Type.dynamic.component", BLATHER, error_message)
      raise ModuleNotFoundError(error_message)

    # TODO: cost?
    if coverage.Coverage.current():
      try:
        module.__file__ = component._erp5_coverage_filename
      except AttributeError:
        LOG("ERP5Type.dynamic.component", WARNING,
            "No coverage filesystem mapping for %s" % spec.name)

    source_code = component.getTextContent(validated_only=True)
    self.fullname_source_code_dict[spec.name] = source_code
    try:
      code_obj = compile(source_code, module.__file__, 'exec')
      exec(code_obj, module.__dict__)
    except Exception:
      from six import reraise
      reraise(
        ComponentImportError,
        ComponentImportError("Cannot load Component %s:\n%s" % (
          spec.name, traceback.format_exc())),
        sys.exc_info()[2])

    component._hookAfterLoad(module)

    import erp5.component
    erp5.component.ref_manager.add_module(module)

    return module
COMPONENT_MODULE_LOADER_INSTANCE = ComponentModuleLoader()

class ComponentAliasLoader(Loader):
  def create_module(self, _):
    pass

  def exec_module(self, module):
    spec = module.__spec__

    # Import of erp5.component.PACKAGE.REFERENCE: search for the Component
    # with the highest version (ERP5Site version_priority_name_list) if any
    if spec.component_real_fullname is None:
      site = getSite()
      # aq_base() because this should not go up to ERP5Site and trigger
      # side-effects, after all this only check for existence...
      component_tool = aq_base(site.portal_components)
      for version in site.getVersionPriorityNameList():
        id_ = "%s.%s.%s" % (spec.component_package_name,
                            version,
                            spec.component_reference)
        component = getattr(component_tool, id_, None)
        if component is not None and component.getValidationState() in (
            'modified', 'validated'):
          spec.component_real_fullname = "erp5.component.%s.%s_version.%s" % (
            spec.component_package_name, version, spec.component_reference)
          break
      else:
        error_message = "%r: None found in modified/validated state" % spec.name
        LOG("ERP5Type.dynamic.component", BLATHER, error_message)
        raise ModuleNotFoundError(error_message)
    # ... Otherwise this is an import of a module previously found on the
    # filesystem and which has been migrated to ZODB Components and thus we are
    # going to end up here again to resolve erp5.component.PACKAGE.REFERENCE as
    # above...

    try:
      real_module = import_module(spec.component_real_fullname)
    except ImportError:
      raise
    else:
      sys.modules[spec.name] = real_module
      MNAME_MAP[spec.name] = spec.component_real_fullname
COMPONENT_ALIAS_LOADER_INSTANCE = ComponentAliasLoader()

class ComponentMetaPathFinder(MetaPathFinder):
  """TODO: Update
  FINDER MUST *NOT* LOAD ANYTHING FROM ZODB (DEADLOCK)

  In Python < 3.3, the import lock is a global lock for all modules:
  http://bugs.python.org/issue9260

  So, release the import lock acquired by import statement on all hooks to load
  objects from ZODB. When an object is requested from ZEO, it sends a RPC
  request and lets the asyncore thread gets the reply. This reply may be a tuple
  (PICKLE, TID), sent directly to the first thread, or an Exception, which tries
  to import a ZODB module and thus creates a deadlock because of the global
  import lock

  Also, handle the case where find_module() may be called without import
  statement as it does not change anything in sys.modules
  """
  def find_spec(self, fullname, path, target=None):
    # fullname=erp5.component.PACKAGE.*: ZODB Components
    if not path:
      if not fullname.startswith('erp5.component.'):
        return None
    # fullname=Products.PACKAGE.*: Filesystem import backward-compatibility
    else:
      # TODO: Should we filter by `path`?
      # TODO: Where to call createFilesystemImportDict()?
      import erp5.component
      try:
        real_name = erp5.component.filesystem_import_dict[fullname]
      except (TypeError, # filesystem_import_dict not filled yet
              KeyError):
        return None
      else:
        spec = ModuleSpec(fullname, loader=COMPONENT_ALIAS_LOADER_INSTANCE)
        spec.component_real_fullname = real_name
        return spec

    package_name = fullname.split('.', 3)[2]
    if package_name not in COMPONENT_PACKAGE_NAME_SET:
      return None

    spec = None
    name = fullname[len('erp5.component.' + package_name + '.'):]
    # name=VERSION_version.REFERENCE
    if '.' in name:
      try:
        version, reference = name.split('.')
        version = version[:-len('_version')]
      except ValueError:
        return None

      id_ = "%s.%s.%s" % (package_name, version, reference)

      # TODO: Unit Test?
      for override_path in os.environ.get('ERP5_COMPONENT_OVERRIDE_PATH',
                                          '').split(os.pathsep):
        filepath = os.path.join(override_path, id_ + '.py')
        if os.path.isfile(filepath) and os.access(filepath, os.R_OK):
          LOG("ERP5Type.dynamic.component", WARNING, "Using local override %s" % filepath)
          return ModuleSpec(fullname, loader=SourceFileLoader(fullname, filepath))

      origin = 'erp5://portal_components/' + id_
      spec = ModuleSpec(fullname,
                        loader=COMPONENT_MODULE_LOADER_INSTANCE,
                        origin=origin)
      spec.has_location = True # __file__ set to `origin`
      spec.component_id = id_

    # name=VERSION_version => package
    elif name.endswith('_version'):
      spec = ModuleSpec(fullname,
                        loader=COMPONENT_VERSION_PACKAGE_LOADER_INSTANCE,
                        is_package=True)
      spec.component_version_package_name = name[:-len('_version')]

    # name=REFERENCE (alias to HIGHEST_VERSION_AVAILABLE_version.REFERENCE)
    else:
      spec = ModuleSpec(fullname, loader=COMPONENT_ALIAS_LOADER_INSTANCE)
      spec.component_package_name = package_name
      spec.component_reference = name
      spec.component_real_fullname = None

    return spec
