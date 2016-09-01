record_portal_type = record_value.portal_type
mapping = {
'Expense Record':(context.expense_validation_item_module, 'Expense Validation Item'),
}

module, portal_type = mapping[record_portal_type]

if getattr(module, record_value.getDocId(), None) is not None:
  raise ValueError('%s %s' % (module, record_value.getDocId()))

return module.newContent(portal_type=portal_type, id=record_value.getDocId())
