"""Set automatic references on the document.
"""

transaction = state_change['object']

# Get sections.
source_section = transaction.getSourceSection()

# Invoice Reference is automatically filled only for Sale Invoice.
if transaction.getPortalType() == 'Sale Invoice':
  if not transaction.getReference():
    invoice_id_group = ('accounting', 'invoice', source_section)
    invoice_reference = transaction.generateNewId(id_group=invoice_id_group,
                                                  default=1)
    transaction.setReference(invoice_reference)
