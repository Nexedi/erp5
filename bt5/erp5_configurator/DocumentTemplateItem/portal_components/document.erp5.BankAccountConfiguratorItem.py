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
from DateTime import DateTime
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Message import translateString
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem


@zope.interface.implementer(IConfiguratorItem)
class BankAccountConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup bank account. """

  meta_type = 'ERP5 Bank Account Configurator Item'
  portal_type = 'Bank Account Configurator Item'
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
                    , PropertySheet.BankAccount )

  def _checkConsistency(self, fixit=False, **kw):
    organisation_module = self.getPortalObject().organisation_module
    error_list = []

    business_configuration = self.getBusinessConfigurationValue()
    organisation_id = business_configuration.\
                         getGlobalConfigurationAttr('organisation_id')
    organisation = organisation_module.get(organisation_id, None)
    if organisation is not None:
      bank_account_list = organisation.objectValues(portal_type='Bank Account')
      if not bank_account_list:
        error_list.append(self._createConstraintMessage(
           "Bank Account should be created"))

        if fixit:
          bank_account = organisation.newContent(portal_type="Bank Account")

          now = DateTime()
          start_date = self.getStartDate(now)
          stop_date = self.getStopDate(now + (365*10))

          bank_dict = {'bank_account_holder_name' : self.getBankAccountHolderName(),
                  'title': self.getTitle(),
                  'bank_account_key': self.getBankAccountKey(),
                  'bank_account_number': self.getBankAccountNumber(),
                  'bank_code': self.getBankCode(),
                  'bank_country_code': self.getBankCountryCode(),
                  'bic_code': self.getBicCode(),
                  'branch': self.getBranch(),
                  'iban': self.getIban(),
                  'internal_bank_account_number': self.getInternalBankAccountNumber(),
                  'overdraft_facility': self.getOverdraftFacility(),
                  'start_date': start_date,
                  'stop_date': stop_date,
                  }
          bank_account.edit(**bank_dict)

          # store globally bank_account_id
          business_configuration.setGlobalConfigurationAttr(bank_account_id=bank_account.getId())

          if self.portal_workflow.isTransitionPossible(bank_account, 'validate'):
            bank_account.validate(comment=translateString("Validated by Configurator"))

    return error_list
