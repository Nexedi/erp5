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

# There is absolutely no reason to use relative imports when loading a Component
from __future__ import absolute_import # six.PY2

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
from . import aq_method_lock, with_aq_method_lock
from .dynamic_module import PackageType
from types import ModuleType
from zLOG import LOG, BLATHER, WARNING
from Acquisition import aq_base
from importlib import import_module
from Products.ERP5Type.patches.Restricted import MNAME_MAP
from AccessControl.SecurityInfo import _moduleSecurity, _appliedModuleSecurity

# ZODB Component packages (ComponentDynamicPackageType) living in erp5.component
COMPONENT_PACKAGE_NAME_SET = {
  'module',
  'extension',
  'document',
  'interface',
  'mixin',
  'test',
  'tool',
}

# PEP-0451 ("A ModuleSpec Type for the Import System"), introduced in v3.4,
# defines a new way to define Import Hooks Finders/Loaders (ModuleSpec,
# find_spec(), {create,exec}_module() API). This has several advantages, such as
# avoiding duplication of boilerplate code (adding module to sys.modules and to
# its parent module) and storing loader-related information into ModuleSpec
# which is then passed to load_module() (ModuleSpec).
#
# Previously, Import system loaders defined by PEP-0302 ({find,load}_module()
# API, deprecated in v3.10).
#
# Both are supported here, although PEP-0302 implementation has been let as it
# was with minimal changes as we do not care much about it anymore...
USE_COMPONENT_PEP_451_LOADER = sys.version_info >= (3, 4)

if sys.version_info < (3, 6):
  class ModuleNotFoundError(ImportError):
    pass
else:
  from builtins import ModuleNotFoundError

class ComponentVersionPackageType(PackageType):
  """
  Component Version package: erp5.component.PACKAGE.VERSION_version
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
    # -> last_sync=12: C1._load_module_unlocked:
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
  erp5.component: Top-level package for ZODB Components packages
  (COMPONENT_PACKAGE_NAME_SET), keeping references to ZODB Component
  modules:

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
    component_tool = aq_base(getSite().portal_components)
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
  erp5.component.COMPONENT_PACKAGE: Package containing modules loaded
  on-demand through import hooks (sys.meta_path) as defined by PEP-0302 and
  PEP-O451:

  * ComponentMetaPathFinder, registered in sys.meta_path, implements
    find_module() (PEP-0302, PY < 3.4) and find_spec() (PEP-0451, PY > 3.4).

  * Single PEP-0302 ComponentModuleLoader() class (load_module() API) and
    PEP-0451 Component*Loader() classes (create_module() and exec_module()
    API) actually load the modules.

  Each module in this package is actually a pointer (called alias here) to the
  versioned module. For example erp5.component.module.foo is an alias to
  erp5.component.VERSION_version.foo, `foo` being the ZODB Components whose
  priority is the highest as by ERP5Site.version_priority_name_list property
  and where `VERSION_version` is a ComponentVersionPackage.
  """
  def reset_unlocked(self, sub_package=None):
    """
    Reset the content of the current package and its version package as
    well recursively. This method must be called within a lock to avoid
    side-effects.
    """
    if sub_package:
      package = sub_package
    else:
      package = self

      # Clear only once...
      COMPONENT_MODULE_LOADER.fullname_source_code_dict.clear()

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
        self.reset_unlocked(sub_package=module)

      module_name = package.__name__ + '.' + name
      LOG("ERP5Type.dynamic.component_package", BLATHER, "Resetting " + module_name)

      # The module must be deleted first from sys.modules to avoid imports in
      # the meantime
      del sys.modules[module_name]

      delattr(package, name)

class ToolComponentDynamicPackageType(ComponentDynamicPackageType):
  """
  erp5.component.tool: ZODB Component Package holding BaseTool-like *Tool
  Components
  """
  def reset_unlocked(self, *args, **kw):
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

    super(ToolComponentDynamicPackageType, self).reset_unlocked(*args, **kw)

class ComponentModuleInspectLoaderMixin:
  """
  ComponentModuleLoader mixin implementing get_source() for both PEP-0302
  and PEP-0451 implementations.
  """
  fullname_source_code_dict = {}
  @classmethod
  def get_source(cls, fullname):
    """
    PEP-0302 function to get the source code, used mainly by linecache for
    tracebacks, pdb...

    Use internal cache rather than accessing the Component directly as this
    would require accessing ERP5 Site even though the source code may be
    retrieved outside of ERP5 (eg DeadlockDebugguer).
    """
    return cls.fullname_source_code_dict.get(fullname)

# Since PY 3.4, we have ModuleSpec so use it as the fallback definition below is
# very minimal and may not work with CPython internal
try:
  from importlib.machinery import ModuleSpec
  from importlib.abc import MetaPathFinder
except ImportError: # < v3.4
  class ModuleSpec(object):
    """
    Dummy object so that we have a single Finder implementation for both
    PEP-0302 without ModuleSpec and PEP-0451 with ModuleSpec.
    """
    def __init__(self, fullname, loader, origin=None, is_package=False):
      self.fullname = fullname
      self.loader = loader
      self.origin = origin
      self.is_package = is_package

  class MetaPathFinder(object):
    """
    PEP-0451 defines this class, base class of ComponentModuleMetaPathFinder,
    which does not exist in < v3.3. Here we define PEP-0302 find_module():
    since PEP-0451, this is just a wrapper around find_spec().
    """
    def find_module(self, fullname, path=None):
      """
      PEP-0302 Finder. Returns None if it cannot handle the given fullname.
      """
      spec = self.find_spec(fullname, path)
      if spec is None:
        return None

      if path:
        # This has to be done here because cpython2 implementation does not have
        # ModuleNotFoundError nor PathFinder import hook (import of filesystem
        # modules) like PEP-0451 implementation. find_module() returning None is
        # the only way to let importer continues searching for filesystem
        # module...
        import erp5.component
        import_lock_held = global_import_lock.held()
        if import_lock_held:
          global_import_lock.release()
        aq_method_lock.acquire()
        try:
          if erp5.component.filesystem_import_dict is None:
            erp5.component.createFilesystemImportDict()
          if (erp5.component.filesystem_import_dict is None or
              fullname not in erp5.component.filesystem_import_dict):
            return None
        finally:
          aq_method_lock.release()
          # Internal release of import lock at the end of import machinery will
          # fail if the hook is not acquired
          if import_lock_held:
            global_import_lock.acquire()

      return spec.loader

# PEP-0451 Loaders implementation:
#   * ComponentVersionPackageLoader:
#     erp5.component.version_VERSION packages
#   * ComponentModuleAliasLoader:
#     erp5.component.FOO
#     => Alias to erp5.component.VERSION_version.FOO where VERSION is the
#        highest version priority.
#   * ComponentModuleLoader:
#     erp5.component.VERSION_version.FOO
if USE_COMPONENT_PEP_451_LOADER:
  from importlib.abc import Loader, InspectLoader
  from importlib.machinery import SourceFileLoader

  class ComponentVersionPackageLoader(Loader):
    """
    PEP-0451 Loader for erp5.component.PACKAGE.VERSION_version packages
    (__path__ set through is_package=True).

    Version package name has '_version' appended to distinguish them from
    top-level Component modules (Component checkConsistency() forbids Component
    name ending with _version).
    """
    @with_aq_method_lock
    def create_module(self, spec):
      if spec.component_version_package_name not in getSite().getVersionPriorityNameList():
        error_message = "%s: No such version" % spec.name
        # A version package is always an intermediate import so raise
        # ModuleNotFoundError following CPython Import Reference
        LOG("ERP5Type.dynamic.component_package", WARNING, error_message)
        raise ModuleNotFoundError(error_message)
      return ComponentVersionPackageType(spec.name)

    def exec_module(self, _):
      pass
  COMPONENT_VERSION_PACKAGE_LOADER = ComponentVersionPackageLoader()

  class ComponentModuleLoader(ComponentModuleInspectLoaderMixin, InspectLoader):
    """
    Main Loader for ZODB Components: erp5.component.PACKAGE.VERSION_version.FOO

    Since v3.3 (http://bugs.python.org/issue9260), there is per-module lock
    (with deadlock avoidance mechanism) so no need to fiddle with the Global Import
    Lock anymore to prevent deadlock when pulling objects from ZODB with ZEO:

      When an object is requested from ZEO, a RPC request is sent whose reply is
      handled by another thread (asyncore). This reply may be a tuple (PICKLE,
      TID), sent directly to the first thread, or an Exception which then tries
      to import a ZODB module and thus creates a deadlock.
    """
    def create_module(self, _):
      # __name__, __loader__, __package__, __spec__, __path__, __file__ (`origin`)
      # and __cached__ set by `importlib._bootstrap._init_module_attrs()` so
      # nothing to be done here and let importlib does it for us...
      pass

    @with_aq_method_lock
    def exec_module(self, module):
      """
      Here we load objects from ZODB, protected by per-module lock. We
      cannot do it in find_spec() because find_spec() is protected by Global
      Import Lock.

      As much as possible is already done in find_spec() and set on ModuleSpec
      object.
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
        LOG("ERP5Type.dynamic.component_package", WARNING, error_message)
        raise ModuleNotFoundError(error_message)

      if coverage.Coverage.current():
        try:
          module.__file__ = component._erp5_coverage_filename
        except AttributeError:
          LOG("ERP5Type.dynamic.component_package", WARNING,
              "No coverage filesystem mapping for %s" % spec.name)

      source_code = component.getTextContent(validated_only=True)
      self.fullname_source_code_dict[spec.name] = source_code
      try:
        code_obj = compile(source_code, module.__file__, 'exec')
        exec(code_obj, module.__dict__)
      except Exception:
        from six import reraise
        error_message = "Cannot load Component %s" % spec.name
        LOG("ERP5Type.dynamic.component_package", WARNING, error_message, error=True)
        reraise(ImportError, ImportError(error_message), sys.exc_info()[2])

      component._hookAfterLoad(module)

      import erp5.component
      erp5.component.ref_manager.add_module(module)

      return module
  COMPONENT_MODULE_LOADER = ComponentModuleLoader()

  class ComponentAliasLoader(Loader):
    """
    Alias Loader: erp5.component.PACKAGE.FOO

    After finding the ZODB Component with the highest VERSION (as defined by
    version_name_priority_list), the module created by create_module() is
    discarded and replaced in sys.modules by the real Component module (as
    loaded by ComponentModuleLoader).

    This cannot be done otherwise because the module created by create_module()
    is modified (importlib._bootstrap:init_module_attrs()) and we just want the
    alias to be a pointer to the *real* module.
    """
    @with_aq_method_lock
    def create_module(self, spec):
      """
      Access ZODB as early as possible, and possibly bail out early if the
      Component cannot be found) instead of doing it later in exec_module().
      """
      # Otherwise, this *might* be a module migrated from the filesystem, in
      # such case we have to resolve its migrated ZODB Component fullname
      # (erp5.component.PACKAGE.VERSION_version.REFERENCE)
      if spec.component_reference is None:
        import erp5.component
        if erp5.component.filesystem_import_dict is None:
          erp5.component.createFilesystemImportDict()
        try:
          real_unversioned_fullname = erp5.component.filesystem_import_dict[spec.name]
        except (TypeError, KeyError):
          # OK, this is a migrated module after all so raise the same exception
          # as find_spec()...
          raise ModuleNotFoundError('No module named ' + spec.name)
        else:
          (spec.component_package_name,
           spec.component_reference) = real_unversioned_fullname[len('erp5.component.'):].split('.')

      # If erp5.component.PACKAGE.REFERENCE: search for the Component with the
      # highest version (ERP5Site version_priority_name_list) if any
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
          spec.component_version = version
          spec.component_real_fullname = "erp5.component.%s.%s_version.%s" % (
            spec.component_package_name, version, spec.component_reference)
          break
      else:
        raise ModuleNotFoundError("%r: None found in modified/validated state" % spec.name)

      return ModuleType('going_to_be_discarded')

    def exec_module(self, module):
      """
      Resolve the "real", target of the alias and add it to sys.modules
      """
      spec = module.__spec__
      # importlib _find_spec() is going to be called and acquire Global Import
      # Lock but this is not a problem because ComponentMetaPathFinder.find_spec()
      # never pulls any object from ZODB...
      real_module = import_module(spec.component_real_fullname)
      sys.modules[spec.name] = real_module
      MNAME_MAP[spec.name] = spec.component_real_fullname
  COMPONENT_ALIAS_LOADER = ComponentAliasLoader()

# PEP-0302 Loader implementation:
#
# We used to have the loader implementation in ComponentVersionDynamicPackage
# (and thus one hook in sys.meta_path for each Component Package) for the
# following reasons: we could not pass information to load_module() (as we can
# now thanks to ModuleSpec object), we had to implement boilerplate which is
# now implemented by PEP-0451 (such as creating the module and setting it on
# its parent module) and we didn't have per-module lock.
#
# The Loader implementation below could have been refactored to minimize code
# duplication but as this is going to be dropped, keep it as it is...
else: # not USE_COMPONENT_PEP_451_LOADER
  from . import global_import_lock
  class ComponentModuleLoader(ComponentModuleInspectLoaderMixin):
    """Main Loader for ZODB Components: erp5.component.PACKAGE.VERSION_version.FOO

    Since we do not have per-module lock, special care and fiddling has to be
    done with Global Import Lock (see PEP-0451 ComponentModuleLoader() docstring).
    """
    def _getVersionPackage(self, parent_package, version):
      """
      Get the version package (PACKAGE.VERSION_version) for the given version
      and create it if it does not already exist
      """
      # Version are appended with '_version' to distinguish them from top-level
      # Component modules (Component checkConsistency() forbids Component name
      # ending with _version)
      version += '_version'
      version_package = getattr(parent_package, version, None)
      if version_package is None:
        version_package_name = parent_package.__name__ + '.' + version

        version_package = ComponentVersionPackageType(version_package_name)
        sys.modules[version_package_name] = version_package
        setattr(parent_package, version, version_package)

      return version_package

    def _load_module_unlocked(self, fullname):
      """
      Load a module with given fullname (see PEP 302) if it's not already in
      sys.modules. It is assumed that imports are filtered properly in
      find_module().

      Also, when the top-level Component module is requested
      (erp5.component.XXX.COMPONENT_NAME), the Component with the highest
      version priority will be loaded into the Version package
      (erp5.component.XXX.VERSION_version.COMPONENT_NAME. Therefore, the
      top-level Component module will just be an alias of the versioned one.

      As per PEP-302, raise an ImportError if the Loader could not load the
      module for any reason...
      """
      if fullname in sys.modules:
        return sys.modules[fullname]

      if fullname.startswith('Products.'):
        module_fullname_filesystem = fullname
        import erp5.component
        try:
          fullname = erp5.component.filesystem_import_dict[module_fullname_filesystem]
        except (TypeError, KeyError):
          raise RuntimeError("This should never happen (race condition!)")
      else:
        module_fullname_filesystem = None

      package_name = fullname.split('.', 3)[2]
      package_fullname = 'erp5.component.' + package_name
      package = sys.modules[package_fullname]
      name = fullname[len(package_fullname + '.'):]
      site = getSite()

      # name=VERSION_version
      #
      # if only Version package (erp5.component.XXX.VERSION_version) is
      # requested to be loaded, then create it if necessary
      if name.endswith('_version'):
        version = name[:-len('_version')]
        return (version in site.getVersionPriorityNameList() and
                self._getVersionPackage(package, version) or None)

      module_fullname_alias = None
      version_package_name = name[:-len('_version')]

      # name=VERSION_version.REFERENCE: Specific version of the Component
      if '.' in name:
        version, name = name.split('.')
        version = version[:-len('_version')]
        component_id = "%s.%s.%s" % (package_name, version, name)
      # name=REFERENCE: Otherwise find the one with the highest version priority
      else:
        component_tool = aq_base(site.portal_components)
        # Version priority name list is ordered in descending order
        for version in site.getVersionPriorityNameList():
          component_id = "%s.%s.%s" % (package_name, version, name)
          component = getattr(component_tool, component_id, None)
          if component is not None and component.getValidationState() in ('modified',
                                                                          'validated'):
            break
        else:
          raise ModuleNotFoundError("%s: no version of Component %s in Site priority" %
                                    (fullname, name))

        module_fullname_alias = package_fullname + '.' + name

        # Check whether this module has already been loaded before for a
        # specific version, if so, just add it to the upper level
        try:
          module = getattr(getattr(package, version + '_version'), name)
        except AttributeError:
          pass
        else:
          setattr(package, name, module)
          sys.modules[module_fullname_alias] = module
          MNAME_MAP[module_fullname_alias] = module.__name__
          if module_fullname_filesystem is not None:
            sys.modules[module_fullname_filesystem] = module
            MNAME_MAP[module_fullname_filesystem] = module.__name__
          return module

      component = getattr(site.portal_components, component_id)
      relative_url = component.getRelativeUrl()
      if six.PY2:
        module_file = '<' + relative_url + '>'
      else:
        module_file = 'erp5://' + relative_url

      module_fullname = '%s.%s_version.%s' % (package_fullname, version, name)
      module = ModuleType(module_fullname, component.getDescription())

      source_code_str = component.getTextContent(validated_only=True)
      for override_path in os.environ.get('ERP5_COMPONENT_OVERRIDE_PATH', '').split(os.pathsep):
        try:
          local_override_path = os.path.join(override_path, component.getId() + '.py')
          with open(local_override_path) as f:
            source_code_str = f.read()
          module_file = local_override_path
          LOG("ERP5Type.dynamic.component_package", WARNING,
              "Using local override %s" % local_override_path)
          break
        except IOError as e:
          if e.errno != errno.ENOENT:
            raise

      version_package = self._getVersionPackage(package, version)

      # All the required objects have been loaded, acquire import lock to modify
      # sys.modules and execute PEP302 requisites
      with global_import_lock:
        # The module *must* be in sys.modules before executing the code in case
        # the module code imports (directly or indirectly) itself (see PEP 302)
        sys.modules[module_fullname] = module
        if module_fullname_alias:
          sys.modules[module_fullname_alias] = module
        if module_fullname_filesystem is not None:
          sys.modules[module_fullname_filesystem] = module

        # This must be set for imports at least (see PEP 302)
        module.__file__ = module_file
        if coverage.Coverage.current():
          if hasattr(component, '_erp5_coverage_filename'):
            module.__file__ = component._erp5_coverage_filename
          else:
            LOG(
              "ERP5Type.dynamic.component_package",
              WARNING,
              "No coverage filesystem mapping for %s" % (module_fullname_alias or module_fullname))

        # Only useful for get_source(), do it before exec'ing the source code
        # so that the source code is properly display in case of error
        module.__loader__ = self
        module.__path__ = []
        module.__name__ = module_fullname
        self.fullname_source_code_dict[module_fullname] = source_code_str

        try:
          # XXX: Any loading from ZODB while exec'ing the source code will result
          # in a deadlock
          source_code_obj = compile(source_code_str, module.__file__, 'exec')
          exec(source_code_obj, module.__dict__)
        except Exception:
          del sys.modules[module_fullname]
          if module_fullname_alias:
            del sys.modules[module_fullname_alias]
          if module_fullname_filesystem is not None:
            del sys.modules[module_fullname_filesystem]

          error_message = "%s: cannot load Component %s :\n%s" % (fullname, name, traceback.format_exc())
          LOG("ERP5Type.dynamic.component_package", WARNING, error_message)
          reraise(ImportError, ImportError(error_message), sys.exc_info()[2])

        # Add the newly created module to the Version package and add it as an
        # alias to the top-level package as well
        setattr(version_package, name, module)
        if module_fullname_alias:
          setattr(package, name, module)
          MNAME_MAP[module_fullname_alias] = module_fullname
          if module_fullname_filesystem is not None:
            MNAME_MAP[module_fullname_filesystem] = module.__name__

        import erp5.component
        erp5.component.ref_manager.add_module(module)

      component._hookAfterLoad(module)
      return module

    def load_module(self, fullname):
      """
      Make sure that loading module is thread-safe using aq_method_lock to make
      sure that modules do not disappear because of an ongoing reset
      """
      import_lock_held = global_import_lock.held()
      if import_lock_held:
        global_import_lock.release()

      aq_method_lock.acquire()
      try:
        return self._load_module_unlocked(fullname)
      finally:
        aq_method_lock.release()

        # Internal release of import lock at the end of import machinery will
        # fail if the hook is not acquired
        if import_lock_held:
          global_import_lock.acquire()

    # Hack for SourceFileLoader()
    def __call__(self, path, filename):
      return self

  COMPONENT_MODULE_LOADER = ComponentModuleLoader()
  COMPONENT_ALIAS_LOADER = COMPONENT_MODULE_LOADER
  COMPONENT_VERSION_PACKAGE_LOADER = COMPONENT_MODULE_LOADER
  SourceFileLoader = COMPONENT_MODULE_LOADER

class ComponentMetaPathFinder(MetaPathFinder):
  """
  PEP-0451 Finder.
  """
  def find_spec(self, fullname, path=None, target=None):
    """
    Return a ModuleSpec() object if the finder can handle the given module
    specified by `fullname`.

    There *MUST* be no access to ZODB as this method is called by
    importlib._bootstrap:_find_spec() which acquire Global Import Lock and
    thus may lead to deadlock (see ComponentModuleLoader docstring).
    """
    # fullname=erp5.component.PACKAGE.*: ZODB Components
    if not path:
      if not fullname.startswith('erp5.component.'):
        return None
    # fullname=Products.PACKAGE.*: Filesystem import backward-compatibility
    else:
      # All migrated code used to be in Products package. That's all we know for
      # now without filesystem_import_dict, mapping of filesystem module to its
      # migrated ZODB Component source_reference, created on-demand and
      # requiring ZODB access
      import Products
      # XXX: Should we really consider the first one only? For now this is
      #      enough as an ERP5 package is at only place...
      path = path[0]
      for product_path in Products.__path__:
        if path.startswith(product_path):
          spec = ModuleSpec(fullname, loader=COMPONENT_ALIAS_LOADER)
          spec.component_package_name = None
          spec.component_reference = None
          spec.component_real_fullname = None
          return spec
      return None

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

      for override_path in os.environ.get('ERP5_COMPONENT_OVERRIDE_PATH',
                                          '').split(os.pathsep):
        filepath = os.path.join(override_path, id_ + '.py')
        if os.path.isfile(filepath) and os.access(filepath, os.R_OK):
          LOG("ERP5Type.dynamic.component_package", WARNING,
              "Using local override %s" % filepath)
          return ModuleSpec(fullname, loader=SourceFileLoader(fullname, filepath))

      origin = 'erp5://portal_components/' + id_
      spec = ModuleSpec(fullname,
                        loader=COMPONENT_MODULE_LOADER,
                        origin=origin)
      spec.has_location = True # __file__ set to `origin`
      spec.component_id = id_

    # name=VERSION_version => package
    elif name.endswith('_version'):
      spec = ModuleSpec(fullname,
                        loader=COMPONENT_VERSION_PACKAGE_LOADER,
                        is_package=True)
      spec.component_version_package_name = name[:-len('_version')]

    # name=REFERENCE (alias to HIGHEST_VERSION_AVAILABLE_version.REFERENCE)
    else:
      spec = ModuleSpec(fullname, loader=COMPONENT_ALIAS_LOADER)
      spec.component_package_name = package_name
      spec.component_reference = name
      # Require ZODB access so going to be resolve in the Loader
      spec.component_real_fullname = None

    return spec

COMPONENT_META_PATH_FINDER = ComponentMetaPathFinder()
