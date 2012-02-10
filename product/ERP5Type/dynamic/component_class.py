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
    #
    # XXX-arnau: This must use reference rather than ID
    site = getSite()
    component = getattr(site.portal_components.aq_explicit, fullname, None)
    if not (component and
            component.getValidationState() in ('modified', 'validated')):
      return None

    # XXX-arnau: Using the Catalog should be preferred however it is not
    # really possible for two reasons: 1/ the Catalog lags behind the ZODB
    # thus immediately after adding/removing a Component, it will fail to load
    # a Component because of reindexing 2/ this is unsurprisingly really slow
    # compared to a ZODB access.
    #
    # site = getSite()
    # found = list(site.portal_catalog.unrestrictedSearchResults(
    #   reference=name,
    #   portal_type=self._portal_type,
    #   parent_uid=site.portal_components.getUid(),
    #   validation_state=('validated', 'modified')))
    # if not found:
    #   return None

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

    # XXX-arnau: erp5.component.extension.VERSION.REFERENCE perhaps but there
    # should be a a way to specify priorities such as portal_skins maybe?
    component_name = fullname.replace(self._namespace_prefix, '')
    component_id = '%s.%s' % (self._namespace, component_name)
    try:
      # XXX-arnau: Performances (~ 200x slower than direct access to ZODB) and
      # also lag behind the ZODB (e.g. reindexing), so this is certainly not a
      # good solution
      component = site.portal_catalog.unrestrictedSearchResults(
        parent_uid=site.portal_components.getUid(),
        reference=component_name,
        validation_state=('validated', 'modified'),
        portal_type=self._portal_type)[0].getObject()

      # component = getattr(site.portal_components, component_id)
    except IndexError:
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
