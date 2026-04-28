if sum([field['quantity'] for field in listbox]) == 123:
  return context.Base_renderForm(
    'Foo_viewEditableListBoxDialog',
    keep_items={
      'portal_status_message': "Total of quantities should not be 123",
      "portal_status_level": "error",
  })

return context.Base_redirect(
  'Foo_viewEditableListBoxDialog',
  keep_items={
    'portal_status_message': "Action succeeded",
    "portal_status_level": "success",
})
