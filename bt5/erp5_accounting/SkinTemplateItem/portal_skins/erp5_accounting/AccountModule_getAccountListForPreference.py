"""
Allows getting an account list for setting preferred `bank`,
`payable` or `receivable` accounts.

Most of the magic is done in `AccountingTransactionLine_getNodeItemList`,
which cannot be called on its own, so this script creates a
temporary Accounting Line.
"""

portal = context.getPortalObject()

if line_id is None:
  line_id = "accounting_line"

temp_accounting_transaction_line = portal.portal_trash.newContent(
  portal_type="Accounting Transaction Line",
  id=line_id,
  temp_object=True,
)

return temp_accounting_transaction_line.AccountingTransactionLine_getNodeItemList()
