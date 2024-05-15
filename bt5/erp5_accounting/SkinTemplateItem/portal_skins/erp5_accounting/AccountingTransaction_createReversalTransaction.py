""" Create a reversal transaction from current transaction. """

Base_translateString = context.Base_translateString
accounting_module = context.getPortalObject().accounting_module
is_source = context.AccountingTransaction_isSourceView()

if is_source:
  specific_reference = context.getSourceReference()
else:
  specific_reference = context.getDestinationReference()

causality_value_list = context.getCausalityValueList()
causality_value_list.append(context)

reversal = accounting_module.newContent (
    portal_type=context.getPortalType(),
    source_section=context.getSourceSection(),
    destination_section=context.getDestinationSection(),
    source_payment=context.getSourcePayment(),
    destination_payment=context.getDestinationPayment(),
    source_project=context.getSourceProject(),
    destination_project=context.getDestinationProject(),
    source_function=context.getSourceFunction(),
    destination_function=context.getDestinationFunction(),
    source_funding=context.getProperty('source_funding'),
    destination_funding=context.getProperty('destination_funding'),
    source_payment_request=context.getProperty('source_payment_request'),
    destination_payment_request=context.getProperty('destination_payment_request'),
    source_administration=context.getSourceAdministration(),
    destination_administration=context.getDestinationAdministration(),
    title=Base_translateString("Reversal Transaction for ${title}",
                               mapping={'title': context.getTitleOrId()}),
    description=Base_translateString(
  "Reversal Transaction for ${title} (${specific_reference})",
  mapping={'title': context.getTitleOrId(),
           'specific_reference': specific_reference}),
    resource=context.getResource(),
    specialise_list=context.getSpecialiseList(),
    causality_value_list=causality_value_list,
    created_by_builder=1 # XXX to prevent init script to create lines
  )

# copy dates
if date:
  start_date = stop_date = date
else:
  start_date = context.getStartDate()
  stop_date = context.getStopDate()

if start_date:
  reversal.setStartDate(start_date)

if context.getStopDate() != context.getStartDate():
  # stop date is currently acquire from start date.
  # we try not to set a stop date on the reversal if it wasn't set on the
  # original
  reversal.setStopDate(stop_date)

if context.getProperty('payment_mode'):
  reversal.setProperty('payment_mode', context.getProperty('payment_mode'))

line_list = context.AccountingTransaction_getAccountingTransactionLineList(
                portal_type=context.getPortalAccountingMovementTypeList())
if not cancellation_amount:
  line_list.reverse()

if line_list:
  # guess portal_type to create lines
  line_portal_type = line_list[0].getPortalType()

  for line in line_list:
    new_line = reversal.newContent( portal_type=line_portal_type )
    new_line.edit(
      source=line.getSource(portal_type='Account'),
      destination=line.getDestination(portal_type='Account'),
      quantity= - line.getQuantity(), )

    if line.getSourceTotalAssetPrice():
      new_line.setSourceTotalAssetPrice( - line.getSourceTotalAssetPrice() )
    if line.getDestinationTotalAssetPrice():
      new_line.setDestinationTotalAssetPrice(
                                    - line.getDestinationTotalAssetPrice() )

    new_line.setCancellationAmount(cancellation_amount)

    # copy some values if they are defined explicitly on line
    for prop in [ 'source_section', 'destination_section',
                  'source_payment', 'destination_payment',
                  'source_project', 'destination_project',
                  'source_function', 'destination_function',
                  'source_funding', 'destination_funding',
                  'source_payment_request', 'destination_payment_request',
                  'resource', 'product_line', 'string_index' ]:
      if line.getProperty(prop) != context.getProperty(prop):
        new_line.setProperty(prop, line.getProperty(prop))

if plan:
  reversal.plan()

if batch:
  return reversal
else:
  return reversal.Base_redirect('view',
    keep_items=dict(portal_status_message=
               Base_translateString("Reversal Transaction for ${specific_reference} created.",
                                    mapping={'specific_reference': specific_reference})))
