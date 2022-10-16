""" Rounds debit and credit lines on generated transactions, according to
precision of this transaction's resource.

What is expected with this script:

  - All lines are rounded to the currency precision
  - Amount on the receivable accounting line match invoice total price
  - total debit == total credit
  - In reality we probably also want that amount on vat line match invoice vat
  amount, but we have ignored this.
"""
import six
line_list = context.getMovementList(
            portal_type=context.getPortalAccountingMovementTypeList())

# If no "line" found (eg no SIT line), then do nothing. This is in the case where a SIT
# has only Invoice Line and no SIT Line. Otherwise account_type_dict will be empty =>
# asset_line = None => the assert below will fail because getTotalPrice() will returns the
# price of all Invoice Lines...
if not line_list:
  return

account_type_dict = {}
source_exchange_ratio = None
destination_exchange_ratio = None


for line in line_list:
  if not destination_exchange_ratio and line.getDestinationTotalAssetPrice():
    destination_exchange_ratio = line.getDestinationTotalAssetPrice() / line.getQuantity()
  if not source_exchange_ratio and line.getSourceTotalAssetPrice():
    source_exchange_ratio = line.getSourceTotalAssetPrice() / line.getQuantity()

  for account in (line.getSourceValue(portal_type='Account'),
      line.getDestinationValue(portal_type='Account'),):
    account_type_dict.setdefault(line, set()).add(
      account is not None and account.getAccountTypeValue() or None)

# find asset line which will be used later
account_type = context.getPortalObject().portal_categories.account_type
receivable_type = account_type.asset.receivable
payable_type = account_type.liability.payable

asset_line = None
for line, account_type_list in six.iteritems(account_type_dict):
  if receivable_type in account_type_list or payable_type in account_type_list:
    if line.getSourceSection() == context.getSourceSection() and \
        line.getDestinationSection() == context.getDestinationSection():
      asset_line = line
      break

def roundLine(resource, get_method, set_method, exchange_ratio):
  precision = context.getQuantityPrecisionFromResource(resource)
  total_quantity = 0.0
  for line in line_list:
    line_quantity = round(getattr(line, get_method)(), precision)
    getattr(line, set_method)(line_quantity)
    total_quantity += line_quantity

  abs_total_quantity = abs(round(total_quantity, precision))
  # The total quantity should be zero with a little error, if simulation has been
  # completely applied, because the debit and the credit must be balanced. However,
  # this is not the case, if the delivery is divergent, as the builder does not
  # adopt prevision automatically, when a conflict happens between the simulation
  # and user-entered values.
  if abs_total_quantity > 2 * context.restrictedTraverse(resource).getBaseUnitQuantity():
    return

  total_price = round(context.getTotalPrice() * exchange_ratio, precision)
  if not asset_line:
    assert total_price == 0.0 and total_quantity == 0.0, \
      'receivable or payable line not found.'
    return

  # If we have a difference between total credit and total debit, one line is
  # chosen to add or remove this difference. The payable or receivable is chosen
  # only if this line is not matching with invoice total price, because total price
  # comes from all invoice lines (quantity * price) and it is what should be payed.
  # And payable or receivable line is the record in the accounting of what has
  # to be payed. Then, we must not touch it when it already matches.
  # If is not a payable or receivable, vat or other line (ie. income) is used.
  line_to_adjust = None
  if abs_total_quantity != 0:
    if round(abs(getattr(asset_line, get_method)()), precision) != round(abs(context.getTotalPrice()) * exchange_ratio, precision):
      # adjust payable or receivable
      for line in line_list:
        if receivable_type in account_type_dict[line] or \
            payable_type in account_type_dict[line]:
          line_to_adjust = line
          break
    if line_to_adjust is None:
      # VAT
      for line in line_list:
        if receivable_type.refundable_vat in account_type_dict[line] or \
            payable_type.collected_vat in account_type_dict[line]:
          line_to_adjust = line
          break
    if line_to_adjust is None:
      # adjust anything except payable or receivable
      for line in line_list:
        if receivable_type not in account_type_dict[line] and \
            payable_type not in account_type_dict[line]:
          line_to_adjust = line
          break

  if line_to_adjust is not None:
    getattr(line_to_adjust, set_method)(
      round(getattr(line_to_adjust, get_method)() - total_quantity, precision))



resource = context.getResource()
# Round Debit/credit
roundLine(resource, 'getQuantity', 'setQuantity', 1)
# Round source asset price
if source_exchange_ratio:
  source_section_price_currency = context.getSourceSectionValue().getPriceCurrency()
  roundLine(source_section_price_currency, 'getSourceTotalAssetPrice', 'setSourceTotalAssetPrice', source_exchange_ratio)
# Round destination asset price
if destination_exchange_ratio:
  destination_section_price_currency = context.getDestinationSectionValue().getPriceCurrency()
  roundLine(destination_section_price_currency, 'getDestinationTotalAssetPrice', 'setDestinationTotalAssetPrice', destination_exchange_ratio)
