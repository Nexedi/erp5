##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    TAHARA Yusei <yusei@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from warnings import warn
import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Message import translateString
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem
from six import string_types as basestring

@zope.interface.implementer(IConfiguratorItem)
class ServiceConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """Create default service documents."""

  meta_type = 'ERP5 Service Configurator Item'
  portal_type = 'Service Configurator Item'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.ConfiguratorItem )

  def _checkConsistency(self, fixit=False, **kw):
    portal = self.getPortalObject()
    error_list = []
    for service_id, service_dict in iter(self.getConfigurationListList()):
      if isinstance(service_dict, basestring):
        warn(DeprecationWarning,
          "ServiceConfiguratorItem now use (service_id, service_dict) as configuration list")
        service_dict = dict(title=service_dict)

      document = getattr(portal.service_module, service_id, None)
      if document is None:
        error_list.append(self._createConstraintMessage(
          "Service %s should be created"))
        if fixit:
          document = portal.service_module.newContent(portal_type='Service',
                                    id=service_id, **service_dict)
          document.validate(comment=translateString("Validated by Configurator"))

      if document:
        ## add to customer template
        business_configuration = self.getBusinessConfigurationValue()
        self.install(document, business_configuration)

    return error_list
