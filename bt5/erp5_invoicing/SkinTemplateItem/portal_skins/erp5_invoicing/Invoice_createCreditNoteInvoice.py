"""
This script is supposed to be the common denominator for invoice reversing operations.
Instead of extending it, call it from project-specific script and edit returned document (or its lines).
"""
def recursiveCopyLine(to_document, from_document):
  newContent = to_document.newContent
  for line in from_document.objectValues(portal_type='Invoice Line'):
    reverse_line = newContent(
      description=line.getDescription(),
      int_index=line.getIntIndex(),
      portal_type=line.getPortalType(),
      price=line.getPrice(),
      quantity=-line.getQuantity(), # Notice the "-" !
      reference=line.getReference(),
      category_list=line.getCategoryList(),
    )
    recursiveCopyLine(reverse_line, line)
    newCell = reverse_line.newContent
    for cell in line.objectValues(portal_type='Invoice Cell'):
      raise NotImplementedError("NotImplemented: Should do something with %s and %s" % (cell, newCell))

reverse_invoice = context.getParentValue().newContent(
  portal_type=context.getPortalType(),
  created_by_builder=1, # tell init script to not create lines
  # Copy over all Arrow-ish relations
  # XXX: it would be cleaner to query property sheet definition and check it applies to context
  category_list=[x for x in context.getCategoryList() if x.startswith('source') or x.startswith('destination')],
)
# Separate edit to have stable outcome WRT category_list
reverse_invoice.edit(
  causality_value=context,
  specialise_list=context.getSpecialiseList(),
  price_currency_list=context.getPriceCurrencyList(),
  resource_list=context.getResourceList(),
)
recursiveCopyLine(reverse_invoice, context)
return reverse_invoice
