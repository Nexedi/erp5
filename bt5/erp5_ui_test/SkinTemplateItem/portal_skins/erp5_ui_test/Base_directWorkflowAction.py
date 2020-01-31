context.portal_workflow.doActionFor(context , workflow_action, comment='', **kw)
message = 'direct workflow action done.'
return context.Base_redirect('view', keep_items={'portal_status_message': message})
