##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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
# This proopgram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.Delivery import Delivery
from Products.ERP5.Document.AccountingTransaction import AccountingTransaction
from Products.ERP5Type.Utils import convertToMixedCase, convertToUpperCase
from erp5.component.module.BaobabMixin import BaobabMixin

class BankingOperation(BaobabMixin, AccountingTransaction):

  # CMF Type Definition
  meta_type = 'ERP5Banking Banking Operation'
  portal_type = 'Banking Operation'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.BankingOperation
                    , PropertySheet.ItemAggregation
                    , PropertySheet.Amount
                    )
  
  security.declarePrivate('manage_beforeDelete')
  def manage_beforeDelete(self, item, container):
    """
    The right of deleting must be define by workflows
    """
    Delivery.manage_beforeDelete(self, item, container)

  security.declareProtected(Permissions.View, 'getDestinationPaymentInternalBankAccountNumber')
  def getDestinationPaymentInternalBankAccountNumber(self, default=None):
    """
    Getter for internal account number
    """
    dest = self.getDestinationPaymentValue(default)
    if dest is default:
      return default
    else:
      return dest.getInternalBankAccountNumber(default)

  security.declareProtected(Permissions.View, 'getSourcePaymentInternalBankAccountNumber')
  def getSourcePaymentInternalBankAccountNumber(self, default=None):
    """
    Getter for internal account number
    """
    src = self.getSourcePaymentValue(default)
    if src is default:
      return default
    else:
      return src.getInternalBankAccountNumber(default)

  security.declareProtected(Permissions.View, 'setPosted')
  def setPosted(self, value):
    """
    Custom method that's automatically sets the reference
    of the account transfer
    """
    if self.getPortalType()=="Account Transfer":
      self.setReference("posted")
    return self._setPosted(value)
