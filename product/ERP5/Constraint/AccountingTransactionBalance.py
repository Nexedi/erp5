##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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

from Products.ERP5Type.Constraint import Constraint
from Products.ERP5Type.Message import Message
translateString = lambda msg: msg  # just to extract messages

class AccountingTransactionBalance(Constraint):
  """Check that accounting transaction total debit and total credit are equals.
  """
  
  _message_id_list = [ 'message_transaction_not_balanced_for_source',
                       'message_transaction_not_balanced_for_destination' ]
  
  message_transaction_not_balanced_for_source = translateString(
       'Transaction is not balanced.')
  message_transaction_not_balanced_for_destination = translateString(
       'Transaction is not balanced.')

  def checkConsistency(self, obj, fixit=0):
    """Implement here the consistency checker
    """
    error_list = []
    source_sum = 0
    destination_sum = 0
    for line in obj.getMovementList(
          portal_type=obj.getPortalAccountingMovementTypeList()):
      if line.getSourceValue() is not None:
        source_sum += line.getSourceInventoriatedTotalAssetPrice() or 0
      if line.getDestinationValue() is not None:
        destination_sum += \
          line.getDestinationInventoriatedTotalAssetPrice() or 0
    
    source_section = obj.getSourceSectionValue()
    destination_section = obj.getDestinationSectionValue()
    source_precision = destination_precision = 2

    if source_section is not None and\
                 source_section.getPortalType() == 'Organisation':
      source_currency = source_section.getPriceCurrencyValue()
      if source_currency is not None:
        source_precision = source_currency.getQuantityPrecision()
    if round(source_sum, source_precision) != 0:
      error_list.append(self._generateError(obj, self._getMessage(
            'message_transaction_not_balanced_for_source')))

    if destination_section is not None and\
                 destination_section.getPortalType() == 'Organisation':
      destination_currency = destination_section.getPriceCurrencyValue()
      if destination_currency is not None:
        destination_precision = destination_currency.getQuantityPrecision()
    if round(destination_sum, destination_precision) != 0:
      error_list.append(self._generateError(obj, self._getMessage(
              'message_transaction_not_balanced_for_destination')))
    
    return error_list
