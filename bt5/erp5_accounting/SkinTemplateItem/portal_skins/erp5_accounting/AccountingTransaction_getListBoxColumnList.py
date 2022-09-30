"""Returns value for 'columns' fields in accounting transaction listboxs.

If there is more than one mirror_section on lines, the listbox will have an
extra column showing mirror_section_title.
The same for apply for most line categories.
"""
section_set = set((None,))
payment_set = set((None,))
payment_request_set = set((None,))
project_set = set((None,))
resource_set = set((context.getResource(),))
item_set = set((None, ))
movement_type_list = context.getPortalAccountingMovementTypeList()

for line in context.getMovementList(portal_type=movement_type_list):
  resource_set.add(line.getResource())
  item_set.add(line.getAggregate())
  if source:
    section_set.add(line.getDestinationSection())
    payment_set.add(line.getSourcePayment())
    payment_request_set.add(line.getSourcePaymentRequest())
    project_set.add(line.getSourceProject())
  else:
    section_set.add(line.getSourceSection())
    payment_set.add(line.getDestinationPayment())
    payment_request_set.add(line.getDestinationPaymentRequest())
    project_set.add(line.getDestinationProject())

if context.getSourcePayment() or context.getDestinationSection():
  min_payment_count = 2
else:
  min_payment_count = 1

if context.getSourceSection() and context.getDestinationSection():
  min_section_count = 2
else:
  # if we have no mirror_section on the transaction but a mirror_section on
  # a line, we have to show the column
  min_section_count = 1

multiple_sections = len(section_set) > min_section_count
multiple_payment = len(payment_set) > min_payment_count

column_item_list = [('translated_id', 'ID')]
a = column_item_list.append
if source:
  a(('source', 'Account'))
else:
  a(('destination', 'Account'))

if context.AccountingTransactionLine_getFunctionItemList(source=source):
  if source:
    a(('source_function', context.AccountingTransactionLine_getFunctionBaseCategoryTitle()))
  else:
    a(('destination_function', context.AccountingTransactionLine_getFunctionBaseCategoryTitle()))

if context.AccountingTransactionLine_getFundingItemList(source=source):
  if source:
    a(('source_funding', context.AccountingTransactionLine_getFundingBaseCategoryTitle()))
  else:
    a(('destination_funding', context.AccountingTransactionLine_getFundingBaseCategoryTitle()))


if multiple_sections:
  if source:
    a(('getDestinationSectionTitle', 'Third Party'))
  else:
    a(('getSourceSectionTitle', 'Third Party'))
if multiple_payment:
  bank_account_display_method = \
    context.portal_preferences.getPreferredAccountingBankAccountDisplayMethod()
  if source:
    if bank_account_display_method == 'bank_account_title':
      a(('getSourcePaymentTitle', 'Bank Account'))
    else:
      a(('getSourcePaymentReference', 'Bank Account'))
  else:
    if bank_account_display_method == 'bank_account_title':
      a(('getDestinationPaymentTitle', 'Bank Account'))
    else:
      a(('getDestinationPaymentReference', 'Bank Account'))
if len(resource_set) > 1:
  a(('getResourceReference', 'Currency'))

if len(payment_request_set) > 1:
  if source:
    a(('getSourcePaymentRequestTitle', 'Payment Request'))
  else:
    a(('getDestinationPaymentRequestTitle', 'Payment Request'))

min_project_count = 1
if context.getSourceProject() or context.getDestinationProject():
  min_project_count = 2
if force_project or len(project_set) > min_project_count:
  if source:
    a(('getSourceProjectTitle', 'Project'))
  else:
    a(('getDestinationProjectTitle', 'Project'))

if len(item_set) > 1:
  a(('aggregate_title_list', 'Items'))

if source:
  a(('source_debit', 'Debit'))
  a(('source_credit', 'Credit'))
else:
  a(('destination_debit', 'Debit'))
  a(('destination_credit', 'Credit'))

return column_item_list
