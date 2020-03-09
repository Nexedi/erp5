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
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Message import translateString
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class AdvancedPurchaseTradeConditionConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup Rules. """

  meta_type = 'ERP5 Advanced Purchase Trade Condition Configurator Item'
  portal_type = 'Advanced Purchase Trade Condition Configurator Item'
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

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    if fixit:
      portal = self.getPortalObject()
      business_configuration = self.getBusinessConfigurationValue()
      business_process_id = \
        business_configuration.getGlobalConfigurationAttr('business_process_id')

      organisation_id = \
        business_configuration.getGlobalConfigurationAttr('organisation_id')

      currency_id = \
        business_configuration.getGlobalConfigurationAttr('currency_id')

      bank_account_id = \
        business_configuration.getGlobalConfigurationAttr('bank_account_id')

      trade_condition = portal.purchase_trade_condition_module.newContent(
                                            portal_type="Purchase Trade Condition",
                                            reference=self.getReference(),
                                            title=self.getTitle(), )

      trade_condition.setSpecialise("business_process_module/%s" %\
                        business_process_id)

      trade_condition.setDestination("organisation_module/%s" % organisation_id)
      trade_condition.setDestinationSection("organisation_module/%s" % organisation_id)
      trade_condition.setPriceCurrency("currency_module/%s" % currency_id)

      trade_condition.setDestinationDecision("organisation_module/%s" % organisation_id)
      trade_condition.setDestinationAdministration("organisation_module/%s" % organisation_id)
      trade_condition.setDestinationPayment("organisation_module/%s/%s" % (organisation_id, bank_account_id))

      trade_condition.validate(comment=translateString("Validated by Configurator"))

      self.install(trade_condition, business_configuration)

    return ['Purchase Trade Condition with reference %s should be created' % \
        self.getReference(),]
