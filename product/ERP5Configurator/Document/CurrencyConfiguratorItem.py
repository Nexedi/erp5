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
from Products.ERP5Type.Message import translateString
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class CurrencyConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup currency. """

  meta_type = 'ERP5 Currency Configurator Item'
  portal_type = 'Currency Configurator Item'
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
                    , PropertySheet.DublinCore
                    , PropertySheet.Price
                    , PropertySheet.Resource
                    , PropertySheet.Reference )

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    currency_module = self.getPortalObject().currency_module
    error_list = []
    title = self.getTitle()
    reference = self.getReference()
    # XXX FIXME This is not exactly desired behaviour
    currency = self.portal_catalog.getResultValue(id=reference,
                                                  portal_type="Currency")
    if currency is None:
      error_list.append(self._createConstraintMessage(
        "Currency %s should be created" % reference))
      if fixit:
        currency = currency_module.newContent(portal_type = "Currency",
                                            id = reference,
                                            title = title,
                                            reference = reference,
                                            base_unit_quantity=self.getBaseUnitQuantity())
        currency.validate(comment=translateString("Validated by Configurator"))

    if currency:
      business_configuration = self.getBusinessConfigurationValue()
      business_configuration.setGlobalConfigurationAttr(currency_id=currency.getId())
      business_configuration.setGlobalConfigurationAttr(\
        currency_path='currency_module/%s' %currency.getId())
      ## add to customer template
      self.install(currency, business_configuration)

    return error_list
