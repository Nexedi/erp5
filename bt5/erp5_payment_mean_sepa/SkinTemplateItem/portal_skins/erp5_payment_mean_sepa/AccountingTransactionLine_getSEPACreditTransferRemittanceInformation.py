"""Return a text to use as Unstructured RemittanceInformation  for this payment transaction.

This is used in SEPA Credit Transfer export, 2.90 RemittanceInformation

This script is a customization point.
"""
ptg = context.getAggregateValue(portal_type='Payment Transaction Group')

if ptg.getSourcePayment() == context.getSourcePayment():
  third_party = context.getDestinationSectionValue()
else:
  third_party = context.getSourceSectionValue()

third_party_name = third_party.getCorporateName() or third_party.getTitle()

return "{invoice_reference} {third_party_name}".format(
  invoice_reference=context.getParentValue().getCausalityReference() or '',
  third_party_name=third_party_name,
).strip()
