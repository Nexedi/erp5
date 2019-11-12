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
from . import aq_method_lock
from types import ModuleType
from zLOG import LOG, BLATHER, WARNING
from Acquisition import aq_base
from importlib import import_module

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
    self._id_prefix = namespace.rsplit('.', 1)[1]
    self._portal_type = portal_type
    self.__version_suffix_len = len('_version')
    self.__fullname_source_code_dict = {}

    # Add this module to sys.path for future imports
    sys.modules[namespace] = self

    # Add the import hook
    sys.meta_path.append(self)

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

    try:
      site = getSite()

      # __import__ will first try a relative import, for example
      # erp5.component.XXX.YYY.ZZZ where erp5.component.XXX.YYY is the current
      # Component where an import is done
      name = fullname[len(self._namespace_prefix):]
      # name=VERSION_version.REFERENCE
      if '.' in name:
        try:
          version, name = name.split('.')
          version = version[:-self.__version_suffix_len]
        except ValueError:
          return None

        id_ = "%s.%s.%s" % (self._id_prefix, version, name)
        # aq_base() because this should not go up to ERP5Site and trigger
        # side-effects, after all this only check for existence...
        try:
          component_tool = aq_base(site.portal_components)
        except AttributeError:
          # For old sites, just use FS Documents...
          return None

        component = getattr(component_tool, id_, None)
        if component is None or component.getValidationState() not in ('modified',
                                                                       'validated'):
          return None

      # Skip unavailable components, otherwise Products for example could be
      # wrongly considered as importable and thus the actual filesystem class
      # ignored
      #
      # name=VERSION_version
      elif name.endswith('_version'):
        if name[:-self.__version_suffix_len] not in site.getVersionPriorityNameList():
          return None

      # name=REFERENCE
      else:
        try:
          component_tool = aq_base(site.portal_components)
        except AttributeError:
          # For old sites, just use FS Documents...
          return None

        for version in site.getVersionPriorityNameList():
          id_ = "%s.%s.%s" % (self._id_prefix, version, name)
          component = getattr(component_tool, id_, None)
          if component is not None and component.getValidationState() in ('modified',
                                                                          'validated'):
            break
        else:
          return None

      return self

    finally:
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

      module_fullname_alias = self._namespace + '.' + name

      # Check whether this module has already been loaded before for a
      # specific version, if so, just add it to the upper level
      try:
        module = getattr(getattr(self, version + '_version'), name)
      except AttributeError:
        pass
      else:
        setattr(self, name, module)
        sys.modules[module_fullname_alias] = module
        return module

    component = getattr(site.portal_components, component_id)
    relative_url = component.getRelativeUrl()

    module_fullname = '%s.%s_version.%s' % (self._namespace, version, name)
    module = ModuleType(module_fullname, component.getDescription())

    source_code_str = component.getTextContent(validated_only=True)
    version_package = self._getVersionPackage(version)

    # All the required objects have been loaded, acquire import lock to modify
    # sys.modules and execute PEP302 requisites
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

      import erp5.component
      erp5.component.ref_manager.add_module(module)

    finally:
      imp.release_lock()

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
    import_lock_held = True
    try:
      imp.release_lock()
    except RuntimeError:
      import_lock_held = False

    aq_method_lock.acquire()
    try:
      return self.__load_module(fullname)
    finally:
      aq_method_lock.release()

      # Internal release of import lock at the end of import machinery will
      # fail if the hook is not acquired
      if import_lock_held:
        imp.acquire_lock()

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
    fullname = self._namespace + '.' + name
    try:
      # Wrapper around __import__ much faster than calling find_module() then
      # load_module(), and returning module 'name' in contrary to __import__
      # returning 'erp5' (requiring fromlist parameter which is slower)
      return import_module(fullname)
    except ImportError as e:
      if str(e) != "No module named " + name:
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
      # Clear the source code dict only once
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

      # Clear pylint cache
      try:
        from astroid.builder import MANAGER
      except ImportError:
        pass
      else:
        MANAGER.astroid_cache.pop(module_name, None)

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
