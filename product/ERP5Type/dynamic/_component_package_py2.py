# There is absolutely no reason to use relative imports when loading a Component
from __future__ import absolute_import

import errno
import os
import six
import sys
import collections
from six import reraise
import traceback

class ComponentModuleLoader(object):
  fullname_source_code_dict = {}

  @classmethod
  def get_source(self, fullname):
    """
    PEP-302 function to get the source code, used mainly by linecache for
    tracebacks, pdb...

    Use internal cache rather than accessing the Component directly as this
    would require accessing ERP5 Site even though the source code may be
    retrieved outside of ERP5 (eg DeadlockDebugguer).
    """
    return cls.fullname_source_code_dict.get(fullname)

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

      version_package = PackageType(version_package_name)
      sys.modules[version_package_name] = version_package
      setattr(self, version, version_package)

    return version_package

  def __load_module(self, fullname):
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

    name = fullname[len(self._namespace_prefix):]

    # if only Version package (erp5.component.XXX.VERSION_version) is
    # requested to be loaded, then create it if necessary
    if name.endswith('_version'):
      version = name[:-len('_version')]
      return (version in site.getVersionPriorityNameList() and
              self._getVersionPackage(version) or None)

    module_fullname_alias = None
    version_package_name = name[:-len('_version')]

    # If a specific version of the Component has been requested
    if '.' in name:
      try:
        version, name = name.split('.')
        version = version[:-len('_version')]
      except ValueError as error:
        raise ImportError("%s: should be %s.VERSION.COMPONENT_REFERENCE (%s)" % \
                            (fullname, self.__name__, error))

      component_id = "%s.%s.%s" % (self._id_prefix, version, name)

    # Otherwise, find the Component with the highest version priority
    else:
      component_tool = aq_base(site.portal_components)
      # Version priority name list is ordered in descending order
      for version in site.getVersionPriorityNameList():
        component_id = "%s.%s.%s" % (self._id_prefix, version, name)
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
    module_file = '<' + relative_url + '>'

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
      return self.__load_module(fullname)
    finally:
      aq_method_lock.release()

      # Internal release of import lock at the end of import machinery will
      # fail if the hook is not acquired
      if import_lock_held:
        global_import_lock.acquire()

COMPONENT_MODULE_LOADER_INSTANCE = ComponentModuleLoader()
class ComponentMetaPathFinder(object):
  """
  PEP-302 Finder which determines which packages and modules will be handled
  by this class. It must be done carefully to avoid handling packages and
  modules the Loader (load_module()) will not be handled later as the latter
  would raise ImportError...

  As per PEP-302, returns None if this Finder cannot handle the given name,
  perhaps because the Finder of another Component Package could do it or because
  this is a filesystem module...
  """
  def find_module(self, fullname, path=None):
    import erp5.component

    # ZODB Components
    if not path:
      if not fullname.startswith('erp5.component.'):
        return None
    # FS import backward compatibility
    else:
      import erp5.component
      try:
        fullname = erp5.component.filesystem_import_dict[fullname]
      except (TypeError, KeyError):
        return None

    package_name = fullname.split('.', 3)[2]
    if package_name not in COMPONENT_PACKAGE_NAME_CLASS_DICT:
      return None

    import_lock_held = global_import_lock.held()
    if import_lock_held:
      global_import_lock.release()

    try:
      site = getSite()

      if erp5.component.filesystem_import_dict is None:
        erp5.component.createFilesystemImportDict()

      # __import__ will first try a relative import, for example
      # erp5.component.XXX.YYY.ZZZ where erp5.component.XXX.YYY is the current
      # Component where an import is done
      name = fullname[len(self._namespace_prefix):]
      # name=VERSION_version.REFERENCE
      if '.' in name:
        try:
          version, name = name.split('.')
          version = version[:-len('_version')]
        except ValueError:
          return None

        id_ = "%s.%s.%s" % (self._id_prefix, version, name)
        # aq_base() because this should not go up to ERP5Site and trigger
        # side-effects, after all this only check for existence...
        component = getattr(aq_base(site.portal_components), id_, None)
        if component is None or component.getValidationState() not in ('modified',
                                                                       'validated'):
          return None

      # Skip unavailable components, otherwise Products for example could be
      # wrongly considered as importable and thus the actual filesystem class
      # ignored
      #
      # name=VERSION_version
      elif name.endswith('_version'):
        if name[:-len('_version')] not in site.getVersionPriorityNameList():
          return None

      # name=REFERENCE
      else:
        component_tool = aq_base(site.portal_components)
        for version in site.getVersionPriorityNameList():
          id_ = "%s.%s.%s" % (self._id_prefix, version, name)
          component = getattr(component_tool, id_, None)
          if component is not None and component.getValidationState() in ('modified',
                                                                          'validated'):
            break
        else:
          return None

      return COMPONENT_MODULE_LOADER_INSTANCE

    finally:
      # Internal release of import lock at the end of import machinery will
      # fail if the hook is not acquired
      if import_lock_held:
        global_import_lock.acquire()
