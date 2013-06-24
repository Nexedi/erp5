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

from Products.ERP5.ERP5Site import getSite
from types import ModuleType
from zLOG import LOG, BLATHER

class ComponentVersionPackage(ModuleType):
  """
  Component Version package (erp5.component.XXX.VERSION)
  """
  __path__ = []

from Products.ERP5Type.dynamic.import_lock import ImportLock

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
  __lock = ImportLock()

  def __init__(self, namespace, portal_type):
    super(ComponentDynamicPackage, self).__init__(namespace)

    self._namespace = namespace
    self._namespace_prefix = namespace + '.'
    self._portal_type = portal_type
    self.__version_suffix_len = len('_version')
    self.__registry_dict = {}

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
      except AttributeError:
        return {}

      version_priority_set = set(portal.getVersionPriorityNameList())

      # objectValues should not be used for a large number of objects, but
      # this is only done upon reset, moreover using the Catalog is too risky
      # as it lags behind and depends upon objects being reindexed
      with self.__lock:
        for component in component_tool.objectValues(portal_type=self._portal_type):
          # Only consider modified or validated states as state transition will
          # be handled by component_validation_workflow which will take care of
          # updating the registry
          if component.getValidationState() in ('modified', 'validated'):
            version = component.getVersion(validated_only=True)
            # The versions should have always been set on ERP5Site property
            # beforehand
            if version in version_priority_set:
              reference = component.getReference(validated_only=True)
              self.__registry_dict.setdefault(reference, {})[version] = component

    return self.__registry_dict

  def get_source(self, fullname):
    """
    Get the source code of the given module name from the ID defined on the
    dynamic module (setting getTextContent() on the module directly may not
    work properly upon reset and there is no need for performance there as it
    is only used for traceback or pdb anyway)
    """
    module = __import__(fullname, fromlist=[fullname.rsplit('.', 1)[0]],
                        level=0)

    return getattr(getSite().portal_components,
                   module.__file__[1:-1]).getTextContent(validated_only=True)

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

      try:
        component = self._registry_dict[name][version]
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
        component = component_version_dict.get(version)
        if component is not None:
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

    module_fullname = '%s.%s_version.%s' % (self._namespace, version, name)
    module = ModuleType(module_fullname, component.getDescription())

    # The module *must* be in sys.modules before executing the code in case
    # the module code imports (directly or indirectly) itself (see PEP 302)
    sys.modules[module_fullname] = module
    if module_fullname_alias:
      sys.modules[module_fullname_alias] = module

    # This must be set for imports at least (see PEP 302)
    module.__file__ = '<' + component.getId() + '>'

    try:
      component.load(module.__dict__, validated_only=True)
    except Exception, error:
      del sys.modules[module_fullname]
      if module_fullname_alias:
        del sys.modules[module_fullname_alias]

      raise ImportError("%s: cannot load Component %s (%s)" % (fullname,
                                                               name,
                                                               error))

    module.__path__ = []
    module.__loader__ = self
    module.__name__ = module_fullname

    # Add the newly created module to the Version package and add it as an
    # alias to the top-level package as well
    setattr(self._getVersionPackage(version), name, module)
    if module_fullname_alias:
      setattr(self, name, module)

    return module

  def load_module(self, fullname):
    """
    Make sure that loading module is thread-safe using aq_method_lock to make
    sure that modules do not disappear because of an ongoing reset
    """
    with self.__lock:
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
      # Clear the Component registry only once
      self.__registry_dict.clear()
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
