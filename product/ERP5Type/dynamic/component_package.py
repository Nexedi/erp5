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
from . import aq_method_lock
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

# 3.4: PEP-0451 (ModuleSpec)
# 3.6: ModuleNotFoundError new exception
IS_COMPONENT_PY2_LOADER = sys.version_info < (3, 6)

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
    except ImportError as e: # TODO: py2
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

      # Clear only once...
      COMPONENT_MODULE_LOADER_INSTANCE.fullname_source_code_dict.clear()

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

class ComponentModuleInspectLoaderMixin:
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

# Since PY 3.4, we have ModuleSpec so use it as the definition is very minimal
# and may not work with CPython internal
try:
  from importlib.machinery import ModuleSpec
  from importlib.abc import MetaPathFinder
except ImportError: # PY < 3.4
  class ModuleSpec(object):
    def __init__(self, fullname, loader, origin=None, is_package=False):
      self.fullname = fullname
      self.loader = loader
      self.origin = origin
      self.is_package = is_package

  class MetaPathFinder(object):
    def find_module(self, fullname, path=None):
      """PEP-302 Finder which determines which packages and modules will be
      handled by this class. It must be done carefully to avoid handling
      packages and modules the Loader (load_module()) will not be handled later
      as the latter would raise ImportError...

      As per PEP-302, returns None if this Finder cannot handle the given name,
      perhaps because the Finder of another Component Package could do it or
      because this is a filesystem module...
      """
      spec = self.find_spec(fullname, path)
      if spec is None:
        return None
      return spec.loader

if not IS_COMPONENT_PY2_LOADER:
  from importlib.abc import Loader, InspectLoader
  from importlib.machinery import SourceFileLoader

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
  
  class ComponentModuleLoader(ComponentModuleInspectLoaderMixin, InspectLoader):
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
else: # IS_COMPONENT_PY2_LOADER
  class ModuleNotFoundError(ImportError):
    pass

  from . import global_import_lock
  class ComponentModuleLoader(ComponentModuleInspectLoaderMixin):
    """A top-level component is a package as it contains modules, this is
    required to be able to add import hooks (as described in PEP 302) when a in
    the source code of a Component, another Component is imported.

    A Component is loaded when being imported, for example in a Document
    Component with ``import erp5.component.XXX.YYY'', through the Importer
    Protocol (PEP 302), by adding an instance of this class to sys.meta_path and
    through find_module() and load_module() methods. The latter method takes
    care of loading the code into a new module.

    This is required because Component classes do not have any physical location
    on the filesystem, however extra care must be taken for performances because
    load_module() will be called each time an import is done, therefore the loader
    should be added to sys.meta_path as late as possible to keep startup time to
    the minimum.
    """
    def _getVersionPackage(self, version):
      """
      Get the version package (NAMESPACE.VERSION_version) for the given version
      and create it if it does not already exist
      """
      # Version are appended with '_version' to distinguish them from top-level
      # Component modules (Component checkConsistency() forbids Component name
      # ending with _version)
      version += '_version'
      version_package = getattr(self, version, None)
      if version_package is None:
        version_package_name = self.__name__ + '.' + version
  
        version_package = ComponentVersionPackageType(version_package_name)
        sys.modules[version_package_name] = version_package
        setattr(self, version, version_package)
  
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
      site = getSite()
  
      if fullname.startswith('Products.'):
        module_fullname_filesystem = fullname
        import erp5.component
        fullname = erp5.component.filesystem_import_dict[module_fullname_filesystem]
      else:
        module_fullname_filesystem = None
  
      package_name = fullname.split('.', 3)[2]
      name = fullname[len('erp5.component.' + package_name + '.'):]
  
      # name=VERSION_version
      #
      # if only Version package (erp5.component.XXX.VERSION_version) is
      # requested to be loaded, then create it if necessary
      if name.endswith('_version'):
        version = name[:-len('_version')]
        return (version in site.getVersionPriorityNameList() and
                self._getVersionPackage(version) or None)
  
      module_fullname_alias = None
      version_package_name = name[:-len('_version')]
  
      # name=VERSION_version.REFERENCE: Specific version of the Component
      if '.' in name:
        try:
          version, name = name.split('.')
          version = version[:-len('_version')]
        except ValueError as error:
          raise ImportError("%s: should be %s.VERSION.COMPONENT_REFERENCE (%s)" % \
                              (fullname, self.__name__, error))
  
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
          raise ImportError("%s: no version of Component %s in Site priority" % \
                              (fullname, name))
  
        module_fullname_alias = self.__name__ + '.' + name
  
        # Check whether this module has already been loaded before for a
        # specific version, if so, just add it to the upper level
        try:
          module = getattr(getattr(self, version + '_version'), name)
        except AttributeError:
          pass
        else:
          setattr(self, name, module)
          sys.modules[module_fullname_alias] = module
          MNAME_MAP[module_fullname_alias] = module.__name__
          if module_fullname_filesystem:
            sys.modules[module_fullname_filesystem] = module
            MNAME_MAP[module_fullname_filesystem] = module.__name__
          return module
  
      component = getattr(site.portal_components, component_id)
      relative_url = component.getRelativeUrl()
      if six.PY2:
        module_file = '<' + relative_url + '>'
      else:
        module_file = 'erp5://' + relative_url
  
      module_fullname = '%s.%s_version.%s' % (self.__name__, version, name)
      module = ModuleType(module_fullname, component.getDescription())
  
      source_code_str = component.getTextContent(validated_only=True)
      for override_path in os.environ.get('ERP5_COMPONENT_OVERRIDE_PATH', '').split(os.pathsep):
        try:
          local_override_path = os.path.join(override_path, component.getId() + '.py')
          with open(local_override_path) as f:
            source_code_str = f.read()
          module_file = local_override_path
          LOG("component_package", WARNING, "Using local override %s" % local_override_path)
          break
        except IOError as e:
          if e.errno != errno.ENOENT:
            raise
  
      version_package = self._getVersionPackage(version)
  
      # All the required objects have been loaded, acquire import lock to modify
      # sys.modules and execute PEP302 requisites
      with global_import_lock:
        # The module *must* be in sys.modules before executing the code in case
        # the module code imports (directly or indirectly) itself (see PEP 302)
        sys.modules[module_fullname] = module
        if module_fullname_alias:
          sys.modules[module_fullname_alias] = module
        if module_fullname_filesystem:
          sys.modules[module_fullname_filesystem] = module
  
        # This must be set for imports at least (see PEP 302)
        module.__file__ = module_file
        if coverage.Coverage.current():
          if hasattr(component, '_erp5_coverage_filename'):
            module.__file__ = component._erp5_coverage_filename
          else:
            LOG(
              "ERP5Type.Tool.ComponentTool",
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
          if module_fullname_filesystem:
            del sys.modules[module_fullname_filesystem]
  
          reraise(
            ComponentImportError,
            ComponentImportError("%s: cannot load Component %s :\n%s" % (
              fullname, name, traceback.format_exc())),
            sys.exc_info()[2])
  
        # Add the newly created module to the Version package and add it as an
        # alias to the top-level package as well
        setattr(version_package, name, module)
        if module_fullname_alias:
          setattr(self, name, module)
          MNAME_MAP[module_fullname_alias] = module_fullname
          if module_fullname_filesystem:
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
      # In Python < 3.3, the import lock is a global lock for all modules:
      # http://bugs.python.org/issue9260
      #
      # So, release the import lock acquired by import statement on all hooks to
      # load objects from ZODB. When an object is requested from ZEO, it sends a
      # RPC request and lets the asyncore thread gets the reply. This reply may
      # be a tuple (PICKLE, TID), sent directly to the first thread, or an
      # Exception, which tries to import a ZODB module and thus creates a
      # deadlock because of the global import lock
      #
      # Also, handle the case where find_module() may be called without import
      # statement as it does not change anything in sys.modules
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
  
  COMPONENT_MODULE_LOADER_INSTANCE = ComponentModuleLoader()
  COMPONENT_ALIAS_LOADER_INSTANCE = COMPONENT_MODULE_LOADER_INSTANCE
  COMPONENT_VERSION_PACKAGE_LOADER_INSTANCE = COMPONENT_MODULE_LOADER_INSTANCE
  SourceFileLoader = COMPONENT_MODULE_LOADER_INSTANCE

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
  def find_spec(self, fullname, path=None, target=None):
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

# TODO: ModuleNotFoundError, ComponentImportError... => Consistency!
# TODO: *_LOADER_INSTANCE: Use the class directly and @classmethod on {create,exec}_module()