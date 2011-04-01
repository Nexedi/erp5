##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
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
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class SaleTradeConditionConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup Rules. """

  meta_type = 'ERP5 Sale Trade Condition Configurator Item'
  portal_type = 'Sale Trade Condition Configurator Item'
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
                    , PropertySheet.Reference
                    )

  def build(self, business_configuration):
    portal = self.getPortalObject()
    business_process_id = \
       business_configuration.getGlobalConfigurationAttr('business_process_id')

    organisation_id = \
      business_configuration.getGlobalConfigurationAttr('organisation_id')

    currency_id = \
      business_configuration.getGlobalConfigurationAttr('currency_id')

    sale_trade_condition = portal.sale_trade_condition_module.newContent(
                                           portal_type="Sale Trade Condition",
                                           referece=self.getReference(),
                                           title=self.getTitle(),
                                           effective_date=DateTime() - 1,
                                           expiration_date=DateTime() + 10 * 365)

    sale_trade_condition.setSpecialise("business_process_module/%s" %\
                      business_process_id)

    sale_trade_condition.setSource("organisation_module/%s" % organisation_id)
    sale_trade_condition.setSourceSection("organisation_module/%s" % organisation_id)
    sale_trade_condition.setPriceCurrency("currency_module/%s" % currency_id)

    self.install(sale_trade_condition, business_configuration)
