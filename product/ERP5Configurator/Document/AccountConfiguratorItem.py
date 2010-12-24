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

  # Declarative interfaces
  zope.interface.implements(interfaces.IConfiguratorItem)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Account )

  def build(self, business_configuration):
    portal = self.getPortalObject()
    account_module = portal.account_module

    extra_kw = {}
    account_id = getattr(self, 'account_id', None)
    if account_id:
      # XXX FIXME This cause conflict when use configuration
      # more then once.
      #extra_kw['id'] = account_id 
      pass
    account = account_module.newContent(
                portal_type='Account',
                title=self.getTitle(),
                account_type=self.getAccountType(),
                gap=self.getGap(),
                financial_section=self.getFinancialSection(),
                credit_account=self.isCreditAccount(),
                description=self.getDescription(),
                **extra_kw)

    ## add to customer template
    self.install(account, business_configuration)
