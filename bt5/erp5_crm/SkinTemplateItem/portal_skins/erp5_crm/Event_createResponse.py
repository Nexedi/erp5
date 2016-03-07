"""
"""
portal = context.getPortalObject()
module = portal.getDefaultModule(response_event_portal_type)

response = module.newContent(portal_type=response_event_portal_type,
                             source=default_destination or context.getDestination(),
                             destination=context.getSource(),
                             resource=response_event_resource,
                             title=response_event_title,
                             text_content=response_event_text_content,
                             start_date=response_event_start_date,
                             causality_value=context,
                             follow_up_list=context.getFollowUpList(),
                             content_type=response_event_content_type or context.getContentType())

if response_event_notification_message:
  response.Event_setTextContentFromNotificationMessage(
     reference=response_event_notification_message,
      substitution_method_parameter_dict=dict(reply_body=context.getReplyBody(),
                                              reply_subject=context.getReplySubject()))

message = portal.Base_translateString('Response Created.')
if response_workflow_action == 'send':
  response.start()
  return context.Base_redirect(form_id, keep_items={'portal_status_message': message})
elif response_workflow_action == 'plan':
  response.plan()
  return context.Base_redirect(form_id, keep_items={'portal_status_message': message})
elif response_workflow_action == 'deliver':
  response.deliver()
  return response.Base_redirect('view', keep_items={'portal_status_message': message})
elif response_workflow_action == 'draft':
  return response.Base_redirect('view', keep_items={'portal_status_message': message})
else:
  raise NotImplementedError('Do not know what to do')
