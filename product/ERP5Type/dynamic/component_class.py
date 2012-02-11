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

import sys
import threading

from Products.ERP5.ERP5Site import getSite
from types import ModuleType
from zLOG import LOG, INFO

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
  __registry_dict = None

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
    if self.__registry_dict is None:
      try:
        component_tool = getSite().portal_components
      # XXX-arnau: When installing ERP5 site, erp5_core_components has not
      # been installed yet, thus this will obviously failed...
      except AttributeError:
        return {}

      self.__registry_dict = {}
      # XXX-arnau: contentValues should not be used as there may be a large
      # number of objects, but as this is done only once, that should perhaps
      # not be a problem after all, and using the Catalog is too risky as it
      # lags behind and depends upon objects being reindexed
      for component in component_tool.contentValues(portal_type=self._portal_type):
        # Only consider modified or validated states as state transition will
        # be handled by component_validation_workflow which will take care of
        # updating the registry
        if component.getValidationState() in ('modified', 'validated'):
          reference = component.getReference()
          self.__registry_dict[reference] = {
            'component': component,
            'module_name': self._namespace_prefix + reference}

    return self.__registry_dict

  def find_module(self, fullname, path=None):
    # Ignore any absolute imports which does not start with this package
    # prefix, None there means that "normal" sys.path will be used
    if not fullname.startswith(self._namespace_prefix):
      return None

    # __import__ will first try a relative import, for example
    # erp5.component.XXX.YYY.ZZZ where erp5.component.XXX.YYY is the current
    # Component where an import is done
    name = fullname.replace(self._namespace_prefix, '')
    if '.' in name:
      return None

    # Skip components not available, otherwise Products for example could be
    # wrongly considered as importable and thus the actual filesystem class
    # ignored
    if name not in self._registry_dict:
      return None

    return self

  def load_module(self, fullname):
    """
    Load a module with given fullname (see PEP 302)
    """
    if not fullname.startswith(self._namespace_prefix):
      return None

    module = sys.modules.get(fullname, None)
    if module is not None:
      return module

    site = getSite()

    component_name = fullname.replace(self._namespace_prefix, '')
    component_id = '%s.%s' % (self._namespace, component_name)
    try:
      component = self._registry_dict[component_name]['component']
    except KeyError:
      LOG("ERP5Type.dynamic", INFO,
          "Could not find %s or it has not been validated or it has not been "
          "migrated yet?" % component_id)

      return None

    with self._lock:
      new_module = ModuleType(component_id, component.getDescription())

      # The module *must* be in sys.modules before executing the code in case
      # the module code imports (directly or indirectly) itself (see PEP 302)
      sys.modules[component_id] = new_module

      # This must be set for imports at least (see PEP 302)
      new_module.__file__ = "<%s>" % component_name

      try:
        component.load(new_module.__dict__, validated_only=True)
      except Exception, e:
        del sys.modules[component_id]
        raise

      new_module.__path__ = []
      new_module.__loader__ = self
      new_module.__name__ = component_id

      setattr(self, component_name, new_module)
      return new_module
