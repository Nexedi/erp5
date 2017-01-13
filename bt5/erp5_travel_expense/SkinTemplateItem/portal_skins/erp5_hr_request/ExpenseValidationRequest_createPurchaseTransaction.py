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

transaction =  portal.accounting_module.newContent(
  portal_type="Purchase Invoice Transaction",
  title="""Frais %s""" % (context.getReference()), 
  source_section=context.getDestinationDecision(),
  source_project=context.getSourceProject(),
  destination_section=context.getDestinationSection(),
  resource=context.getPriceCurrency(),
  created_by_builder=1,  # XXX this prevent init script from creating lines.
  start_date=context.getStartDate(),
  causality=context.getRelativeUrl(),
)

transaction.newContent(
  portal_type='Purchase Invoice Transaction Line',
  destination=mission_account,
  quantity= (float(context.getTotalPrice())),
)

transaction.newContent(
  portal_type='Purchase Invoice Transaction Line',
  destination=debt_account,
  quantity=(-float(context.getTotalPrice())),
)

transaction.stop()

return transaction.getRelativeUrl()
