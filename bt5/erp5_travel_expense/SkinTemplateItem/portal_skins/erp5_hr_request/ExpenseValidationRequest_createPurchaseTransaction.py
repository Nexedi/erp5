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
  destination_project=context.getSourceProject(),
  destination_section=context.getSourceSection(),
  resource=context.getPriceCurrency(),
  created_by_builder=1,  # XXX this prevent init script from creating lines.
  start_date=context.getStartDate(),
  stop_date=context.getStartDate(),
  causality=context.getRelativeUrl(),
)

document = context.getFollowUpRelatedValue(portal_type=['PDF', 'Image'])
if document:
  document.setFollowUpValueList(document.getFollowUpValueList() + [transaction])

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

from Products.ERP5Type.Core.Workflow import ValidationFailed
from zExceptions import Redirect
try:
  transaction.Base_checkConsistency()
except ValidationFailed, error_message:
  if getattr(error_message, 'msg', None):
    # use of Message class to store message+mapping+domain
    message = error_message.msg
    if same_type(message, []):
      message = '. '.join('%s' % x for x in message)
    else:
      message = str(message)
  else:
    message = str(error_message)
  if len(message) > 2000: # too long message will generate a too long URI
                          # that would become an error.
    message = "%s ..." % message[:(2000 - 4)]
  context.Base_redirect(keep_items={'portal_status_message':message})

transaction.confirm()

return transaction.getRelativeUrl()
