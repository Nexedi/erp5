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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Message import translateString
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem


@zope.interface.implementer(IConfiguratorItem)
class AccountConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup an Accounting Account. """

  meta_type = 'ERP5 Account Configurator Item'
  portal_type = 'Account Configurator Item'
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
                    , PropertySheet.Account )

  def _checkConsistency(self, fixit=False, **kw):
    account_module = self.getPortalObject().account_module
    account = None
    account_id = getattr(self, 'account_id', None)

    error_list = []
    error_list_append = lambda msg: error_list.append(
        self._createConstraintMessage(msg))
    extra_kw = {}
    if account_id:
      extra_kw['id'] = account_id
      account = getattr(account_module, account_id, None)

    if account is None:
      error_list_append("Account %s should be created" % self.getTitle())
      if fixit:
        account = account_module.newContent(
                    portal_type='Account',
                    title=self.getTitle(),
                    account_type=self.getAccountType(),
                    gap=self.getGap(),
                    financial_section=self.getFinancialSection(),
                    credit_account=self.isCreditAccount(),
                    description=self.getDescription(),
                    **extra_kw)
    else:
      error_list_append("Account %s should be updated" % account.getRelativeUrl())
      if fixit:
        # Update existing account
        if (self.getAccountType() != account.getAccountType()) and \
            (self.getFinancialSection() != account.getFinancialSection()):
          raise ValueError("The Configurator is trying to overwrite previous configuration information (%s)" % account.getRelativeUrl())

        account.edit(title=self.getTitle(), description=self.getDescription())
        gap_list = account.getGapList()
        # Only include only the additional gap that do not collide.
        if self.getGap() not in gap_list:
          gap_list.append(self.getGap())
          account.setGapList(gap_list)
        account.setCreditAccount(self.isCreditAccount())

    if account and fixit:
      if self.portal_workflow.isTransitionPossible(account, 'validate'):
        account.validate(comment=translateString("Validated by Configurator"))

      ## add to customer template
      business_configuration = self.getBusinessConfigurationValue()
      self.install(account, business_configuration)

    return error_list
