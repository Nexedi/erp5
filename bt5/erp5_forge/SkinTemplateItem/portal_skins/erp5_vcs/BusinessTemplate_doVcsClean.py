context.getVcsTool().clean()

return context.Base_redirect('view', keep_items={
  'portal_status_message': 'Working copy cleaned successfully.'
})
