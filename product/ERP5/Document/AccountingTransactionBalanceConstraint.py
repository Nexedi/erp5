##############################################################################
#
# Copyright (c) 2007-2010 Nexedi SA and Contributors. All Rights Reserved.
#                         Jerome Perrin <jerome@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from Products.ERP5Type.mixin.constraint import ConstraintMixin
from Products.ERP5Type import PropertySheet

class AccountingTransactionBalanceConstraint(ConstraintMixin):
  """
  Check that accounting transaction total debit and total credit are equal.

  This is only relevant for ZODB Property Sheets (filesystem Property
  Sheets rely on Products.ERP5.Constraint.AccountingTransactionBalance
  instead).
  """
  meta_type = 'ERP5 Accounting Transaction Balance Constraint'
  portal_type = 'Accounting Transaction Balance Constraint'

  property_sheets = ConstraintMixin.property_sheets + \
                    (PropertySheet.AccountingTransactionBalanceConstraint,)

  def _checkConsistency(self, obj, fixit=0):
    """
    Check the object's consistency
    """
    error_list = []
    source_sum = {}
    destination_sum = {}
    for line in obj.getMovementList(
          portal_type=obj.getPortalAccountingMovementTypeList()):
      if line.getSourceValue(portal_type='Account') is not None:
        section = line.getSourceSectionValue()
        source_sum[section] = source_sum.get(section, 0) + \
            (line.getSourceInventoriatedTotalAssetPrice() or 0)
      if line.getDestinationValue(portal_type='Account') is not None:
        section = line.getDestinationSectionValue()
        destination_sum[section] = destination_sum.get(section, 0) + \
          (line.getDestinationInventoriatedTotalAssetPrice() or 0)

    for section, total in source_sum.items():
      precision = 2
      if section is not None and\
          section.getPortalType() == 'Organisation':
        section_currency = section.getPriceCurrencyValue()
        if section_currency is not None:
          precision = section_currency.getQuantityPrecision()
        if round(total, precision) != 0:
          error_list.append(self._generateError(obj, self._getMessage(
                'message_transaction_not_balanced_for_source'),
                mapping=dict(section_title=section.getTranslatedTitle())))
          break

    for section, total in destination_sum.items():
      precision = 2
      if section is not None and\
          section.getPortalType() == 'Organisation':
        section_currency = section.getPriceCurrencyValue()
        if section_currency is not None:
          precision = section_currency.getQuantityPrecision()
        if round(total, precision) != 0:
          error_list.append(self._generateError(obj, self._getMessage(
                'message_transaction_not_balanced_for_destination'),
                mapping=dict(section_title=section.getTranslatedTitle())))
          break

    return error_list

  _message_id_tuple = ('message_transaction_not_balanced_for_source',
                       'message_transaction_not_balanced_for_destination')
