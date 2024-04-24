from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.CMFCore.WorkflowCore import WorkflowException

o = context.getObject()

try :
  context.portal_workflow.doActionFor( o,
    workflow_action,
    comment=comment,
    **kw)
except WorkflowException:
  pass
except ValidationFailed as message:
  if getattr(message, 'msg', None) and same_type(message.msg, []):
    message = '. '.join('%s' % x for x in message.msg)
  if not batch :
    return context.Base_redirect(keep_items={'portal_status_message': str(message)})
