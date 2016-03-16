from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.CMFCore.WorkflowCore import WorkflowException

o = context.getObject()

if 1: # keep indentation
  try : 
    context.portal_workflow.doActionFor( o,
     workflow_action,
     comment=comment,
     **kw)
  except WorkflowException:
    pass
  except ValidationFailed, message:
    if getattr(message, 'msg', None) and same_type(message.msg, []):
      message = '. '.join('%s' % x for x in message.msg)
    if not batch :
      context.REQUEST.RESPONSE.redirect(
                 "%s/view?portal_status_message=%s" %
                 (context.absolute_url(), message))
