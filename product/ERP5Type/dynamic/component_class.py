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

from Products.ERP5.ERP5Site import getSite
from types import ModuleType

class ComponentModule(ModuleType):
  _resetting = False
  _last_reset = -1

  def __getattribute__(self, name):
    """
    Synchronize between ZEO clients

    XXX-arnau: surely bad from a performance POV and not thread-safe
    """
    if name[0] == '_' or self._resetting:
      return super(ComponentModule, self).__getattribute__(name)

    import erp5.component
    site = getSite()
    cookie = site.getCacheCookie('component_classes')
    if self._last_reset == -1:
      self._last_reset = site.getCacheCookie('component_classes')
    elif cookie != self._last_reset:
      self._resetting = True
      site.portal_components.reset(is_sync=True)
      self._resetting = False

    return super(ComponentModule, self).__getattribute__(name)

from types import ModuleType
from zLOG import LOG, INFO

def generateComponentClassWrapper(namespace):
  def generateComponentClass(component_name):
    site = getSite()

    component_id = '%s.%s' % (namespace, component_name)
    try:
      component = getattr(site.portal_components, component_id)
    except AttributeError:
      LOG("ERP5Type.dynamic", INFO,
          "Could not find %s, perhaps it has not been migrated yet?" % \
            component_id)

      raise
    else:
      if component.getValidationState() == 'validated':
        new_module = ModuleType(component_name,
                                component.getDescription())

        component.load(new_module.__dict__)
        LOG("ERP5Type.dynamic", INFO, "Loaded successfully %s" % component_id)
        return new_module
      else:
        raise AttributeError("Component %s not validated" % component_id)

  return generateComponentClass
