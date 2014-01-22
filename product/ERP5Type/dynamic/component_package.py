# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SARL and Contributors. All Rights Reserved.
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

# There is absolutely no reason to use relative imports when loading a Component
from __future__ import absolute_import

import sys
import imp
import collections

from Products.ERP5.ERP5Site import getSite
from Products.ERP5Type.Globals import get_request
from . import aq_method_lock
from types import ModuleType
from zLOG import LOG, BLATHER

class ComponentVersionPackage(ModuleType):
  """
  Component Version package (erp5.component.XXX.VERSION)
  """
  __path__ = []

class ComponentDynamicPackage(ModuleType):
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
  # Necessary otherwise imports will fail because an object is considered a
  # package only if __path__ is defined
  __path__ = []

  def __init__(self, namespace, portal_type):
    super(ComponentDynamicPackage, self).__init__(namespace)

    self._namespace = namespace
    self._namespace_prefix = namespace + '.'
    self._portal_type = portal_type
    self.__version_suffix_len = len('_version')
    self.__registry_dict = collections.defaultdict(dict)
    self.__fullname_source_code_dict = {}

    # Add this module to sys.path for future imports
    sys.modules[namespace] = self

    # Add the import hook
    sys.meta_path.append(self)

  @property
  def _registry_dict(self):
    """
    Create the component registry, this is very similar to
    Products.ERP5Type.document_class_registry and avoids checking whether a
    Component exists at each call at the expense of being slower when being
    re-generated after a reset. Moreover, it allows to handle reference
    easily.
    """
    if not self.__registry_dict:
      portal = getSite()

      try:
        component_tool = portal.portal_components
      # When installing ERP5 site, erp5_core_components has not been installed
      # yet, thus this will obviously failed...
      #
      # XXX-arnau: Is this needed as it is now done in synchronizeDynamicModules?
      except AttributeError:
        return {}

      version_priority_set = set(portal.getVersionPriorityNameList())

      # objectValues should not be used for a large number of objects, but
      # this is only done upon reset, moreover using the Catalog is too risky
      # as it lags behind and depends upon objects being reindexed
      for component in component_tool.objectValues(portal_type=self._portal_type):
        # Only consider modified or validated states as state transition will
        # be handled by component_validation_workflow which will take care of
        # updating the registry
        try:
          validation_state_tuple = component.getValidationState()
        except AttributeError:
          # XXX: Accessors may have not been generated yet
          pass
        else:
          if validation_state_tuple in ('modified', 'validated'):
            version = component.getVersion(validated_only=True)
            # The versions should have always been set on ERP5Site property
            # beforehand
            if version in version_priority_set:
              reference = component.getReference(validated_only=True)
              self.__registry_dict[reference][version] = (component.getId(),
                                                          component._p_oid)

    return self.__registry_dict

  def get_source(self, fullname):
    """
    PEP-302 function to get the source code, used mainly by linecache for
    tracebacks, pdb...

    Use internal cache rather than accessing the Component directly as this
    would require accessing ERP5 Site even though the source code may be
    retrieved outside of ERP5 (eg DeadlockDebugguer).
    """
    return self.__fullname_source_code_dict.get(fullname)

  def find_module(self, fullname, path=None):
    """
    PEP-302 Finder which determines which packages and modules will be handled
    by this class. It must be done carefully to avoid handling packages and
    modules the Loader (load_module()) will not be handled later as the latter
    would raise ImportError...

    As per PEP-302, returns None if this Finder cannot handle the given name,
    perhaps because the Finder of another Component Package could do it or
    because this is a filesystem module...
    """
    # Ignore imports with a path which are filesystem-only and any
    # absolute imports which does not start with this package prefix,
    # None there means that "normal" sys.path will be used
    if path or not fullname.startswith(self._namespace_prefix):
      return None

    import_lock_held = True
    try:
      imp.release_lock()
    except RuntimeError:
      import_lock_held = False

    # The import lock has been released, but as _registry_dict may be
    # initialized or cleared, no other Components should access this critical
    # region
    #
    # TODO-arnau: Too coarse-grain?
    aq_method_lock.acquire()
    try:
      site = getSite()

      # __import__ will first try a relative import, for example
      # erp5.component.XXX.YYY.ZZZ where erp5.component.XXX.YYY is the current
      # Component where an import is done
      name = fullname[len(self._namespace_prefix):]
      if '.' in name:
        try:
          version, name = name.split('.')
          version = version[:-self.__version_suffix_len]
        except ValueError:
          return None

        try:
          self._registry_dict[name][version]
        except KeyError:
          return None

      # Skip unavailable components, otherwise Products for example could be
      # wrongly considered as importable and thus the actual filesystem class
      # ignored
      elif (name not in self._registry_dict and
            name[:-self.__version_suffix_len] not in site.getVersionPriorityNameList()):
        return None

      return self

    finally:
      aq_method_lock.release()

      # Internal release of import lock at the end of import machinery will
      # fail if the hook is not acquired
      if import_lock_held:
        imp.acquire_lock()

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
      version_package_name = self._namespace + '.' + version

      version_package = ComponentVersionPackage(version_package_name)
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
    # statement as it does change anything in sys.modules
    import_lock_held = True
    try:
      imp.release_lock()
    except RuntimeError:
      import_lock_held = False

    try:
      site = getSite()
      name = fullname[len(self._namespace_prefix):]

      # if only Version package (erp5.component.XXX.VERSION_version) is
      # requested to be loaded, then create it if necessary
      if name.endswith('_version'):
        version = name[:-self.__version_suffix_len]
        return (version in site.getVersionPriorityNameList() and
                self._getVersionPackage(version) or None)

      module_fullname_alias = None
      version_package_name = name[:-self.__version_suffix_len]

      # If a specific version of the Component has been requested
      if '.' in name:
        try:
          version, name = name.split('.')
          version = version[:-self.__version_suffix_len]
        except ValueError, error:
          raise ImportError("%s: should be %s.VERSION.COMPONENT_REFERENCE (%s)" % \
                              (fullname, self._namespace, error))

        try:
          component_id = self._registry_dict[name][version][0]
        except KeyError:
          raise ImportError("%s: version %s of Component %s could not be found" % \
                              (fullname, version, name))

      # Otherwise, find the Component with the highest version priority
      else:
        try:
          component_version_dict = self._registry_dict[name]
        except KeyError:
          raise ImportError("%s: Component %s could not be found" % (fullname,
                                                                     name))

        # Version priority name list is ordered in descending order
        for version in site.getVersionPriorityNameList():
          component_id_uid_tuple = component_version_dict.get(version)
          if component_id_uid_tuple is not None:
            component_id = component_id_uid_tuple[0]
            break
        else:
          raise ImportError("%s: no version of Component %s in Site priority" % \
                              (fullname, name))

        # Check whether this module has already been loaded before for a
        # specific version, if so, just add it to the upper level
        try:
          module = getattr(getattr(self, version + '_version'), name)
        except AttributeError:
          pass
        else:
          setattr(self, name, module)
          return module

        module_fullname_alias = self._namespace + '.' + name

      component = getattr(site.portal_components, component_id)
      relative_url = component.getRelativeUrl()

      module_fullname = '%s.%s_version.%s' % (self._namespace, version, name)
      module = ModuleType(module_fullname, component.getDescription())

      source_code_str = component.getTextContent(validated_only=True)
      version_package = self._getVersionPackage(version)

    finally:
      # Internal release of import lock at the end of import machinery will
      # fail if the hook is not acquired
      if import_lock_held:
        imp.acquire_lock()

    # All the required objects have been loaded, acquire import lock to modify
    # sys.modules and execute PEP302 requisites
    if not import_lock_held:
      imp.acquire_lock()
    try:
      # The module *must* be in sys.modules before executing the code in case
      # the module code imports (directly or indirectly) itself (see PEP 302)
      sys.modules[module_fullname] = module
      if module_fullname_alias:
        sys.modules[module_fullname_alias] = module

      # This must be set for imports at least (see PEP 302)
      module.__file__ = '<' + relative_url + '>'

      # Only useful for get_source(), do it before exec'ing the source code
      # so that the source code is properly display in case of error
      module.__loader__ = self
      module.__path__ = []
      module.__name__ = module_fullname
      self.__fullname_source_code_dict[module_fullname] = source_code_str

      try:
        # XXX: Any loading from ZODB while exec'ing the source code will result
        # in a deadlock
        source_code_obj = compile(source_code_str, module.__file__, 'exec')
        exec source_code_obj in module.__dict__
      except Exception, error:
        del sys.modules[module_fullname]
        if module_fullname_alias:
          del sys.modules[module_fullname_alias]

        raise ImportError(
          "%s: cannot load Component %s (%s)" % (fullname, name, error)), \
          None, sys.exc_info()[2]

      # Add the newly created module to the Version package and add it as an
      # alias to the top-level package as well
      setattr(version_package, name, module)
      if module_fullname_alias:
        setattr(self, name, module)

      # When the reference counter of a module reaches 0, its globals are all
      # reset to None. So, if a thread performs a reset while another one
      # executes codes using globals (such as modules imported at module level),
      # the latter one must keep a reference around to avoid reaching a
      # reference count to 0. Thus, add it to Request object.
      #
      # OTOH, this means that ZODB Components module *must* be imported at the
      # top level, otherwise a module being relied upon may have a different API
      # after rset, thus it may fail...
      request_obj = get_request()
      module_cache_set = getattr(request_obj, '_module_cache_set', None)
      if module_cache_set is None:
        module_cache_set = set()
        request_obj._module_cache_set = module_cache_set

      module_cache_set.add(module)

      return module
    finally:
      # load_module() can be called outside of import machinery, for example
      # to check first if the module can be handled by Component and then try
      # to load it without going through the same code again
      if not import_lock_held:
        imp.release_lock()

  def load_module(self, fullname):
    """
    Make sure that loading module is thread-safe using aq_method_lock to make
    sure that modules do not disappear because of an ongoing reset
    """
    with aq_method_lock:
      return self.__load_module(fullname)

  def reset(self, sub_package=None):
    """
    Reset the content of the current package and its version package as well
    recursively. This method must be called within a lock to avoid side
    effects
    """
    if sub_package:
      package = sub_package
    else:
      # Clear the Component registry and source code dict only once
      self.__registry_dict.clear()
      self.__fullname_source_code_dict.clear()
      package = self

    for name, module in package.__dict__.items():
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
