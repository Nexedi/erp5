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
import threading

from Products.ERP5.ERP5Site import getSite
from types import ModuleType
from zLOG import LOG, INFO

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
  __registry_dict = {}

  def __init__(self, namespace, portal_type):
    super(ComponentDynamicPackage, self).__init__(namespace)

    self._namespace = namespace
    self._namespace_prefix = namespace + '.'
    self._portal_type = portal_type

    self._lock = threading.RLock()

    # Add this module to sys.path for future imports
    sys.modules[namespace] = self

    # Add the import hook
    sys.meta_path.append(self)

  @property
  def _registry_dict(self):
    """
    Create the component registry, this is very similar to
    Products.ERP5Type.document_class_registry and avoids checking whether a
    Component exists at each call at the expense to increase startup
    time. Moreover, it allows to handle reference easily.

    XXX-arnau: handle different versions of a Component, perhaps something
    like erp5.component.extension.VERSION.REFERENCE perhaps but there should
    be a a way to specify priorities such as portal_skins maybe?
    """
    if not self.__registry_dict:
      try:
        component_tool = getSite().portal_components
      # XXX-arnau: When installing ERP5 site, erp5_core_components has not
      # been installed yet, thus this will obviously failed...
      except AttributeError:
        return {}

      # XXX-arnau: contentValues should not be used as there may be a large
      # number of objects, but as this is done only once, that should perhaps
      # not be a problem after all, and using the Catalog is too risky as it
      # lags behind and depends upon objects being reindexed
      for component in component_tool.contentValues(portal_type=self._portal_type):
        # Only consider modified or validated states as state transition will
        # be handled by component_validation_workflow which will take care of
        # updating the registry
        if component.getValidationState() in ('modified', 'validated'):
          reference = component.getReference(validated_only=True)
          version = component.getVersion(validated_only=True)
          self.__registry_dict.setdefault(reference, {})[version] = component

    return self.__registry_dict

  def _resetRegistry(self):
    self.__registry_dict.clear()

  def find_module(self, fullname, path=None):
    # Ignore imports with a path which are filesystem-only and any
    # absolute imports which does not start with this package prefix,
    # None there means that "normal" sys.path will be used
    if path or not fullname.startswith(self._namespace_prefix):
      return None

    site = getSite()

    # __import__ will first try a relative import, for example
    # erp5.component.XXX.YYY.ZZZ where erp5.component.XXX.YYY is the current
    # Component where an import is done
    name = fullname.replace(self._namespace_prefix, '')
    if '.' in name:
      try:
        version, name = name.split('.')
        version = version.replace('_version', '')
      except ValueError:
        return None

      try:
        self._registry_dict[name][version]
      except KeyError:
        return None

    # Skip components not available, otherwise Products for example could be
    # wrongly considered as importable and thus the actual filesystem class
    # ignored
    elif (name not in self._registry_dict and
          name.replace('_version', '') not in site.getVersionPriority()):
      return None

    return self

  def _getVersionPackage(self, version):
    version += '_version'
    version_package = getattr(self, version, None)
    if version_package is None:
      version_package_name = '%s.%s' % (self._namespace, version)

      version_package = ComponentVersionPackage(version_package_name)
      sys.modules[version_package_name] = version_package
      setattr(self, version, version_package)

    return version_package

  def load_module(self, fullname):
    """
    Load a module with given fullname (see PEP 302) if it's not
    already in sys.modules. It is assumed that imports are filtered
    properly in find_module().
    """
    site = getSite()
    component_name = fullname.replace(self._namespace_prefix, '')
    if component_name.endswith('_version'):
      version = component_name.replace('_version', '')
      return (version in site.getVersionPriority() and
              self._getVersionPackage(version) or None)

    component_id_alias = None
    version_package_name = component_name.replace('_version', '')
    if '.' in component_name:
      try:
        version, component_name = component_name.split('.')
        version = version.replace('_version', '')
      except ValueError:
        return None

      try:
        component = self._registry_dict[component_name][version]
      except KeyError:
        LOG("ERP5Type.dynamic", INFO,
            "Could not find version %s of Component %s" % (version,
                                                           component_name))
        return None

    else:
      try:
        component_version_dict = self._registry_dict[component_name]
      except KeyError:
        LOG("ERP5Type.dynamic", INFO,
          "Could not find Component " + component_name)

        return None

      for version in site.getVersionPriority():
        component = component_version_dict.get(version, None)
        if component is not None:
          break

      if component is None:
        return None

      try:
        module = getattr(getattr(self, version + '_version'), component_name)
      except AttributeError:
        pass
      else:
        with self._lock:
          setattr(self._getVersionPackage(version), component_name, module)

        return module

      component_id_alias = '%s.%s' % (self._namespace, component_name)

    component_id = '%s.%s_version.%s' % (self._namespace, version,
                                         component_name)

    with self._lock:
      new_module = ModuleType(component_id, component.getDescription())

      # The module *must* be in sys.modules before executing the code in case
      # the module code imports (directly or indirectly) itself (see PEP 302)
      sys.modules[component_id] = new_module
      if component_id_alias:
        sys.modules[component_id_alias] = new_module

      # This must be set for imports at least (see PEP 302)
      new_module.__file__ = "<%s>" % component_name

      try:
        component.load(new_module.__dict__, validated_only=True)
      except:
        del sys.modules[component_id]
        if component_id_alias:
          del sys.modules[component_id_alias]

        raise

      new_module.__path__ = []
      new_module.__loader__ = self
      new_module.__name__ = component_id

      setattr(self._getVersionPackage(version), component_name, new_module)
      if component_id_alias:
        setattr(self, component_name, new_module)

      return new_module
