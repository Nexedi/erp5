##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class CustomerBT5ConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Create a new bt5 for customer configuration.

      This business template is not installed locally, only build.
  """

  meta_type = 'ERP5 Customer BT5 Configurator Item'
  portal_type = 'Customer BT5 Configurator Item'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IConfiguratorItem)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore )

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    template_tool = self.getPortalObject().portal_templates
    error_list = []
    if self.bt5_title not in template_tool.getBuiltBusinessTemplateList():
      error_list.append(self._createConstraintMessage(
        '%s should be created' % self.bt5_title))

    if fixit:
      bt5 = template_tool.newContent(portal_type="Business Template",
          title=self.bt5_title)
      business_configuration = self.getBusinessConfigurationValue()
      business_configuration.setSpecialise(bt5.getRelativeUrl())

    return error_list
