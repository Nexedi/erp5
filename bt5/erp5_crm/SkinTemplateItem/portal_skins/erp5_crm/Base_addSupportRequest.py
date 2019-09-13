portal = context.getPortalObject()
logged_in_user_value = portal.portal_membership.getAuthenticatedMember().getUserValue()
now = DateTime()

if support_request_template:
  support_request_template = portal.restrictedTraverse(support_request_template)
  # Note: temlate's reference is first event's Portal Type for such template.
  # This is not so clean, but is far cheaper than creating a
  # "first_event_portal_type" base category, adding it to Support Request and
  # then cleaning up such category on instance creation from template.
  event_portal_type = support_request_template.getReference()
  container = portal.support_request_module
  support_request = container[
    container.manage_pasteObjects(
      support_request_template.getParentValue().manage_copyObjects(
        ids=[support_request_template.getId()],
      ),
    )[0]['new_id']
  ]
  support_request.makeTemplateInstance()
else:
  support_request = portal.support_request_module.newContent(
    portal_type='Support Request',
    title=title,
    resource=support_request_resource,
  )
support_request.edit(
  source_value=logged_in_user_value,
  source_section=portal.portal_preferences.getPreferredSection(),
  destination_decision_value=context,
  start_date=now,
)

context_portal_type = context.getPortalType()
if context_portal_type == 'Person':
  source = context
  source_section = context.getSubordinationValue()
elif context_portal_type == 'Organisation':
  source = source_section = context
else:
  source = source_section = None

event = portal.getDefaultModule(portal_type=event_portal_type).newContent(
  portal_type=event_portal_type,
  title=support_request.getTitle(),
  resource=resource,
  source_value=source,
  source_section_value=source_section,
  destination_value=logged_in_user_value,
  destination_section_value=None if logged_in_user_value is None else logged_in_user_value.getSubordinationValue(),
  start_date=now,
  follow_up_value=support_request,
  text_content=text_content,
  content_type='text/html' if portal.portal_preferences.getPreferredTextEditor() else 'text/plain',
)
support_request.setCausalityValue(event)
# Note: workflow can be event_workflow or event_simulation_workflow.
# The former allows "deliver" from "started" only, so use this state.
event.start()
event.deliver()

for method_id in {
      'submitted': ('submit', ),
      'validated': ('validate', ),
      'suspended': ('validate', 'suspend'),
      'invalidated': ('validate', 'invalidate'),
    }[support_request_state]:
  getattr(support_request, method_id)()

return support_request.Base_redirect(
  keep_items={
    'portal_status_message': portal.Base_translateString(
      'New ${portal_type} created.',
      mapping={
        'portal_type': portal.Base_translateString('Support Request'),
      },
    ),
  },
)
