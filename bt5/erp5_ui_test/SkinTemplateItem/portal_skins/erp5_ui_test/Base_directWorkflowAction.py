request = context.REQUEST
context.portal_workflow.doActionFor(context , workflow_action, comment='', **kw)
message = 'direct workflow action done.'
request.RESPONSE.redirect("%s/?portal_status_message=%s" % (context.absolute_url(), message) )
