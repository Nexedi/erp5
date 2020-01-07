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
from Products.ERP5.Document.InventoryLine import InventoryLine
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.Container import Container
from Products.ERP5.Document.AccountingTransaction import AccountingTransaction
from AccessControl.PermissionRole import PermissionRole
from Products.ERP5Type.Utils import convertToMixedCase, convertToUpperCase
from erp5.component.module.BaobabMixin import BaobabMixin

# Import classes to monkey-patch
# XXX All patches must be moved in a Business Template !!
from Products.ERP5.Document.Currency import Currency
from Products.ERP5.Document.DeliveryCell import DeliveryCell


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
### Dynamic patch
Delivery.getBaobabSourceUid = lambda x: x.getSourceUid()
Delivery.getBaobabSourceUid__roles__ = PermissionRole(Permissions.View)

Delivery.getBaobabDestinationUid = lambda x: x.getDestinationUid()
Delivery.getBaobabDestinationUid__roles__ = PermissionRole(Permissions.View)

Delivery.getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
Delivery.getBaobabSourceSectionUid__roles__ = PermissionRole(Permissions.View)

Delivery.getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
Delivery.getBaobabDestinationSectionUid__roles__ = PermissionRole(Permissions.View)

Delivery.getBaobabSourcePaymentUid = lambda x: x.getSourcePaymentUid()
Delivery.getBaobabSourcePaymentUid__roles__ = PermissionRole(Permissions.View)

Delivery.getBaobabDestinationPaymentUid = lambda x: x.getDestinationPaymentUid()
Delivery.getBaobabDestinationPaymentUid__roles__ = PermissionRole(Permissions.View)

Delivery.getBaobabSourceFunctionUid = lambda x: x.getSourceFunctionUid()
Delivery.getBaobabSourceFunctionUid__roles__ = PermissionRole(Permissions.View)

Delivery.getBaobabDestinationFunctionUid = lambda x: x.getDestinationFunctionUid()
Delivery.getBaobabDestinationFunctionUid__roles__ = PermissionRole(Permissions.View)

Delivery.getBaobabSourceProjectUid = lambda x: x.getSourceProjectUid()
Delivery.getBaobabSourceProjectUid__roles__ = PermissionRole(Permissions.View)

Delivery.getBaobabDestinationProjectUid = lambda x: x.getDestinationProjectUid()
Delivery.getBaobabDestinationProjectUid__roles__ = PermissionRole(Permissions.View)

### Overload Movement
Movement.getBaobabSourceUid = lambda x: x.getSourceUid()
Movement.getBaobabSourceUid__roles__ = PermissionRole(Permissions.View)

Movement.getBaobabDestinationUid = lambda x: x.getDestinationUid()
Movement.getBaobabDestinationUid__roles__ = PermissionRole(Permissions.View)

Movement.getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
Movement.getBaobabSourceSectionUid__roles__ = PermissionRole(Permissions.View)

Movement.getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
Movement.getBaobabDestinationSectionUid__roles__ = PermissionRole(Permissions.View)

Movement.getBaobabSourcePaymentUid = lambda x: x.getSourcePaymentUid()
Movement.getBaobabSourcePaymentUid__roles__ = PermissionRole(Permissions.View)

Movement.getBaobabDestinationPaymentUid = lambda x: x.getDestinationPaymentUid()
Movement.getBaobabDestinationPaymentUid__roles__ = PermissionRole(Permissions.View)

Movement.getBaobabSourceFunctionUid = lambda x: x.getSourceFunctionUid()
Movement.getBaobabSourceFunctionUid__roles__ = PermissionRole(Permissions.View)

Movement.getBaobabDestinationFunctionUid = lambda x: x.getDestinationFunctionUid()
Movement.getBaobabDestinationFunctionUid__roles__ = PermissionRole(Permissions.View)

Movement.getBaobabSourceProjectUid = lambda x: x.getSourceProjectUid()
Movement.getBaobabSourceProjectUid__roles__ = PermissionRole(Permissions.View)

Movement.getBaobabDestinationProjectUid = lambda x: x.getDestinationProjectUid()
Movement.getBaobabDestinationProjectUid__roles__ = PermissionRole(Permissions.View)

### Acquire Baobab source / destination uids from parent line
DeliveryCell.getBaobabSourceUid = lambda x: x.getSourceUid()
DeliveryCell.getBaobabSourceUid__roles__ = PermissionRole(Permissions.View)

DeliveryCell.getBaobabDestinationUid = lambda x: x.getDestinationUid()
DeliveryCell.getBaobabDestinationUid__roles__ = PermissionRole(Permissions.View)

DeliveryCell.getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
DeliveryCell.getBaobabSourceSectionUid__roles__ = PermissionRole(Permissions.View)

DeliveryCell.getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
DeliveryCell.getBaobabDestinationSectionUid__roles__ = PermissionRole(Permissions.View)

DeliveryCell.getBaobabSourcePaymentUid = lambda x: x.getSourcePaymentUid()
DeliveryCell.getBaobabSourcePaymentUid__roles__ = PermissionRole(Permissions.View)

DeliveryCell.getBaobabDestinationPaymentUid = lambda x: x.getDestinationPaymentUid()
DeliveryCell.getBaobabDestinationPaymentUid__roles__ = PermissionRole(Permissions.View)

DeliveryCell.getBaobabSourceFunctionUid = lambda x: x.getSourceFunctionUid()
DeliveryCell.getBaobabSourceFunctionUid__roles__ = PermissionRole(Permissions.View)

DeliveryCell.getBaobabDestinationFunctionUid = lambda x: x.getDestinationFunctionUid()
DeliveryCell.getBaobabDestinationFunctionUid__roles__ = PermissionRole(Permissions.View)

DeliveryCell.getBaobabSourceProjectUid = lambda x: x.getSourceProjectUid()
DeliveryCell.getBaobabSourceProjectUid__roles__ = PermissionRole(Permissions.View)

DeliveryCell.getBaobabDestinationProjectUid = lambda x: x.getDestinationProjectUid()
DeliveryCell.getBaobabDestinationProjectUid__roles__ = PermissionRole(Permissions.View)



### Dynamic patch
Container.getBaobabSourceUid = lambda x: x.getSourceUid()
Container.getBaobabSourceUid__roles__ = PermissionRole(Permissions.View)

Container.getBaobabDestinationUid = lambda x: x.getDestinationUid()
Container.getBaobabDestinationUid__roles__ = PermissionRole(Permissions.View)

Container.getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
Container.getBaobabSourceSectionUid__roles__ = PermissionRole(Permissions.View)

Container.getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
Container.getBaobabDestinationSectionUid__roles__ = PermissionRole(Permissions.View)

Container.getBaobabSourcePaymentUid = lambda x: x.getSourcePaymentUid()
Container.getBaobabSourcePaymentUid__roles__ = PermissionRole(Permissions.View)

Container.getBaobabDestinationPaymentUid = lambda x: x.getDestinationPaymentUid()
Container.getBaobabDestinationPaymentUid__roles__ = PermissionRole(Permissions.View)

Container.getBaobabSourceFunctionUid = lambda x: x.getSourceFunctionUid()
Container.getBaobabSourceFunctionUid__roles__ = PermissionRole(Permissions.View)

Container.getBaobabDestinationFunctionUid = lambda x: x.getDestinationFunctionUid()
Container.getBaobabDestinationFunctionUid__roles__ = PermissionRole(Permissions.View)

Container.getBaobabSourceProjectUid = lambda x: x.getSourceProjectUid()
Container.getBaobabSourceProjectUid__roles__ = PermissionRole(Permissions.View)

Container.getBaobabDestinationProjectUid = lambda x: x.getDestinationProjectUid()
Container.getBaobabDestinationProjectUid__roles__ = PermissionRole(Permissions.View)


### Dynamic patch
InventoryLine.getBaobabSourceUid = lambda x: x.getSourceUid()
InventoryLine.getBaobabSourceUid__roles__ = PermissionRole(Permissions.View)

InventoryLine.getBaobabDestinationUid = lambda x: x.getDestinationUid()
InventoryLine.getBaobabDestinationUid__roles__ = PermissionRole(Permissions.View)

InventoryLine.getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
InventoryLine.getBaobabSourceSectionUid__roles__ = PermissionRole(Permissions.View)

InventoryLine.getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
InventoryLine.getBaobabDestinationSectionUid__roles__ = PermissionRole(Permissions.View)

InventoryLine.getBaobabSourcePaymentUid = lambda x: x.getSourcePaymentUid()
InventoryLine.getBaobabSourcePaymentUid__roles__ = PermissionRole(Permissions.View)

InventoryLine.getBaobabDestinationPaymentUid = lambda x: x.getDestinationPaymentUid()
InventoryLine.getBaobabDestinationPaymentUid__roles__ = PermissionRole(Permissions.View)

InventoryLine.getBaobabSourceFunctionUid = lambda x: x.getSourceFunctionUid()
InventoryLine.getBaobabSourceFunctionUid__roles__ = PermissionRole(Permissions.View)

InventoryLine.getBaobabDestinationFunctionUid = lambda x: x.getDestinationFunctionUid()
InventoryLine.getBaobabDestinationFunctionUid__roles__ = PermissionRole(Permissions.View)

InventoryLine.getBaobabSourceProjectUid = lambda x: x.getSourceProjectUid()
InventoryLine.getBaobabSourceProjectUid__roles__ = PermissionRole(Permissions.View)

InventoryLine.getBaobabDestinationProjectUid = lambda x: x.getDestinationProjectUid()
InventoryLine.getBaobabDestinationProjectUid__roles__ = PermissionRole(Permissions.View)

