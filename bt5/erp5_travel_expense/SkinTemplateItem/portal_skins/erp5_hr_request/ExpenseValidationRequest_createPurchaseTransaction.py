portal = context.getPortalObject()
state = context.getSimulationState()
if (state not in ('accepted')):
  from zExceptions import Unauthorized
  raise Unauthorized

mission_account, debt_account = portal.ERP5Site_getPreferredExpenseAccountTuple()
if not mission_account:
  return context.Base_redirect('view',
    keep_items=dict(
      portal_status_message=portal.Base_translateString(
        "No Account has been defined for Expenses Transactions",
      ),
    )
  )

currency = context.getPriceCurrencyValue()
transaction =  portal.accounting_module.newContent(
  portal_type="Purchase Invoice Transaction",
  source_section=context.getDestinationDecision(),
  destination_project=context.getSourceProject(),
  destination_section=context.getSourceSection(),
  resource_value=currency,
  created_by_builder=1,  # XXX this prevent init script from creating lines.
  start_date=context.getStartDate(),
  stop_date=context.getStartDate(),
  causality=context.getRelativeUrl(),
)
transaction.setTitle("Frais %s" % context.getReference())

document = context.getFollowUpRelatedValue(portal_type=['PDF', 'Image'])
if document:
  document.setFollowUpValueList(document.getFollowUpValueList() + [transaction])

precision = 2
if currency is not None:
  precision = currency.getQuantityPrecision()

amount = round(context.getTotalPrice(), precision)

transaction.newContent(
  portal_type='Purchase Invoice Transaction Line',
  destination=mission_account,
  quantity=amount,
)

transaction.newContent(
  portal_type='Purchase Invoice Transaction Line',
  destination=debt_account,
  quantity=-amount,
)

from Products.ERP5Type.Core.Workflow import ValidationFailed
try:
  transaction.AccountingTransaction_checkConsistency()
except ValidationFailed:
  pass
else:
  transaction.confirm()

return transaction.getRelativeUrl()
