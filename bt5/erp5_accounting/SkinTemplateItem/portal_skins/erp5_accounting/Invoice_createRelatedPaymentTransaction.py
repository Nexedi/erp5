"""Create a related payment transaction, using the account `node`, the payment
`payment`, and setting the payment mode `payment_mode`. An optional `date` can
be provided, but by default the transaction is created at the system date.
"""
from DateTime import DateTime
# translate with Base_translateString which is a bit more robust during
# activities, because it doesn't rely on REQUEST['PARENTS']
Base_translateString = context.Base_translateString

if date is None:
  date = DateTime()
portal = context.getPortalObject()
payment_dict = {}
is_source = context.AccountingTransaction_isSourceView()
line_portal_type = 'Accounting Transaction Line'

# update selection params, because it'll be used in the selection dialog.
portal.portal_selections.setSelectionParamsFor(
          'accounting_create_related_payment_selection',
          params=dict(node_for_related_payment=node,
                      payment_mode_for_related_payment=payment_mode,
                      payment_for_related_payment=payment))


# Calculate the payable/receivable quantity, using
# Invoice_getRemainingTotalPayablePrice script.
total_payable_price_details = \
          context.Invoice_getRemainingTotalPayablePrice(detailed=True,
                                                        quantity=True)

# if there's nothing more to pay, don't create an empty transaction
if sum(total_payable_price_details.values()) == 0:
  if not batch_mode:
    return context.REQUEST.RESPONSE.redirect(
      "%s/view?portal_status_message=%s" % (
      context.absolute_url(), Base_translateString('Nothing more to pay.')))
  return None

related_payment = portal.accounting_module.newContent(
  portal_type="Payment Transaction",
  title=str(Base_translateString("Payment of ${invoice_title}",
          mapping=dict(invoice_title=unicode((context.getReference() or
                                              context.getTitle() or ''),
                                              'utf8', 'repr')))),
  source_section=context.getSourceSection(),
  destination_section=context.getDestinationSection(),
  source_project=context.getSourceProject(),
  destination_project=context.getDestinationProject(),
  source_function=context.getSourceFunction(),
  destination_function=context.getDestinationFunction(),
  stop_date=date,
  start_date=date,
  resource=context.getResource(),
  causality_value=context,
  created_by_builder=1, # XXX this prevent init script from creating lines.
  payment_mode=payment_mode,
)
if is_source:
  related_payment.edit(destination_payment=context.getDestinationPayment(),
                       source_payment=payment)
  section = context.getSourceSection()
  mirror_section = context.getDestinationSection()
else:
  related_payment.edit(destination_payment=payment,
              source_payment=context.getSourcePayment())
  section = context.getDestinationSection()
  mirror_section = context.getSourceSection()

bank = related_payment.newContent(
   portal_type=line_portal_type,
   id='bank',
)
bank_quantity = 0

for (line_node, line_mirror_section), quantity in\
                        total_payable_price_details.items():
  if line_mirror_section == mirror_section:
    bank_quantity += quantity
    if is_source:
      line = related_payment.newContent(
        portal_type=line_portal_type,
        source=line_node,
        quantity=quantity)
    else:
      line = related_payment.newContent(
        portal_type=line_portal_type,
        destination=line_node,
        quantity=-quantity)

if is_source:
  bank.edit( source=node,
             quantity=-bank_quantity )
else:
  bank.edit( destination=node,
             quantity=bank_quantity )

if plan:
  related_payment.plan()

if not batch_mode:
  return context.REQUEST.RESPONSE.redirect(
    "%s/view?portal_status_message=%s" % (
    related_payment.absolute_url(),
    Base_translateString('Related payment created.')))
else:
  return related_payment
