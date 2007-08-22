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
  isPortalContent = 1
  isRADContent = 1

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
                    )

  # Declarative interfaces
  __implements__ = ( )

  security.declarePrivate('_setSource')
  def _setSource(self, value, portal_type=None):
    """ 
      Set the source Account and implicitely the destination Account
    using the source's mirror account.
    """
    self._setCategoryMembership('source', value, base=0)
    if self.getPortalType() not in \
            self.getPortalBalanceTransactionLineTypeList() \
            and value not in (None, ''):
      source = self.getPortalObject().portal_categories.resolveCategory(value)
      destination = self.getDestination()
      if source is not None:
        mirror_list = source.getDestinationList()
      else:
        mirror_list = []
      if len(mirror_list) > 0 and destination not in mirror_list:
        self._setCategoryMembership('destination', mirror_list[0], base=0)

  security.declareProtected(Permissions.ModifyPortalContent, 'setSource')
  def setSource(self, value):
    """
      Set the source Account and implicitely the destination Account
    using the source's mirror account, then reindex self.
    """
    self._setSource(value)
    self.reindexObject()
  
  security.declarePrivate('_setDestination')
  def _setDestination(self, value, portal_type=None):
    """
      Set the destination Account and implicitely the source Account
    using the source's mirror account.
    """
    self._setCategoryMembership('destination', value, base=0)
    if self.getPortalType() not in \
            self.getPortalBalanceTransactionLineTypeList()\
            and value not in (None, ''):
      destination = self.getPortalObject().\
                        portal_categories.resolveCategory(value)
      source = self.getSource()
      if destination is not None:
        mirror_list = destination.getDestinationList()
      else:
        mirror_list = []
      if len(mirror_list) > 0 and source not in mirror_list:
        self._setCategoryMembership('source', mirror_list[0], base=0)

  security.declareProtected(Permissions.ModifyPortalContent, 'setDestination')
  def setDestination(self, value):
    """ 
      Set the destination Account and implicitely the source Account
    using the source's mirror account, then reindex self.
    """
    self._setDestination(value)
    self.reindexObject()

  security.declarePrivate('_edit')
  def _edit(self, REQUEST = None, force_update = 0, **kw):
    """ 
      Edit the object and set source/destination using magic methods.
    """
    if kw.has_key('source'):
      self._setSource(kw['source'])
    elif kw.has_key('destination') :
      self._setDestination(kw['destination'])
    DeliveryLine._edit(self, REQUEST=REQUEST, force_update=force_update, **kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoriatedQuantity')
  def getInventoriatedQuantity(self):
    """
      Redefine this method here, because AccountingTransactionLine does
      not have target values.
    """
    return Amount.getInventoriatedQuantity(self)


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoriatedStartDate')
  def getInventoriatedStartDate(self):
    """
      Get the start date.
    """
    return self.getStartDate()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoriatedStopDate')
  def getInventoriatedStopDate(self):
    """
      Get the stop date.
    """
    return self.getStopDate()
 
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
      conversion manually in accounting.  This is required by accounting
      law. One can not account USD (in a EUR based company) without
      defining the equivalent in EUR.
    """
    return 1.0

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDestinationAssetPrice')
  def getDestinationAssetPrice(self):
    """
      The price is set to 1.0 because we do not want to implement
      automatic currency conversion in accounting. Users must define the
      conversion manually in accounting.  This is required by accounting
      law. One can not account USD (in a EUR based company) without
      defining the equivalent in EUR.
    """
    return 1.0
