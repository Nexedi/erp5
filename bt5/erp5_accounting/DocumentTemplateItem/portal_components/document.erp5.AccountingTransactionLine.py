##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.DeliveryLine import DeliveryLine
from Products.ERP5.Document.Amount import Amount


class AccountingTransactionLine(DeliveryLine):
  """
  Accounting Transaction Lines allow to move some quantity of money from
  a source to a destination
  """

  meta_type = 'ERP5 Accounting Transaction Line'
  portal_type = 'Accounting Transaction Line'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Price
                    , PropertySheet.PaymentCondition
                    )


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoriatedQuantity')
  def getInventoriatedQuantity(self):
    """
      Redefine this method here, because AccountingTransactionLine does
      not have target values.
    """
    return Amount.getInventoriatedQuantity(self)

  # Pricing in standard currency
  security.declareProtected(Permissions.AccessContentsInformation, 'getPrice')
  def getPrice(self, context=None):
    """
      On accounting transaction lines, the price is always set to 1.
      We use the `quantity` property for the default quantity, and the
      converted value for source in getSourceInventoriatedTotalAssetPrice
      and getDestinationInventoriatedTotalAssetPrice for destination.
    """
    return 1.0

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSourceAssetPrice')
  def getSourceAssetPrice(self):
    """
      The price is set to 1.0 because we do not want to implement
      automatic currency conversion in accounting. Users must define the
      conversion manually in accounting. One can not account USD (in a EUR
      based company) without defining the equivalent in EUR.
    """
    return 1.0

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDestinationAssetPrice')
  def getDestinationAssetPrice(self):
    """
      The price is set to 1.0 because we do not want to implement
      automatic currency conversion in accounting. Users must define the
      conversion manually in accounting. One can not account USD (in a EUR
      based company) without defining the equivalent in EUR.
    """
    return 1.0

  security.declareProtected(Permissions.AccessContentsInformation,
                            'setGroupingReference')
  def setGroupingReference(self, value):
    # Sets the grouping reference.
    # This method is redefined here to override security definition.
    # In the case of an accounting transaction line, we want to be able to
    # set a grouping reference on a line after the point where we remove the
    # Modify portal content permission, as long as this method cannot be called
    # directly from the URL, that's why this method is without docstring.
    self._baseSetGroupingReference(value)
    self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'setGroupingDate')
  def setGroupingDate(self, value):
    # Sets the grouping date.
    # See also setGroupingReference.
    self._baseSetGroupingDate(value)
    self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isMovingItem')
  def isMovingItem(self, item):
    """
      We often like to aggregate items to Accounting Transaction Line
      for traceability, but this movements does not physically move the item
      to the destination of this account.
    """
    return False
