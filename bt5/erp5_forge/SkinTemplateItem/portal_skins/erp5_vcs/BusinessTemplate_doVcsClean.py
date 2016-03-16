context.getVcsTool().clean()

context.REQUEST.set('portal_status_message', 'Working copy cleaned successfully.')
return context.view()
