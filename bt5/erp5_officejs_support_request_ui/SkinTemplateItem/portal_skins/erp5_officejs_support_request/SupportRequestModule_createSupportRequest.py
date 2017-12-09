portal = context.getPortalObject()
logged_in_user_value = portal.portal_membership.getAuthenticatedMember().getUserValue()

now = DateTime()

# default_field_your_resource,field_your_title, description, field_your_project, default_field_your_project, form_id, field_your_resource, dialog_id, resource, title, file, project, dialog_method, field_my_description, field_your_file=None
project_list = portal.portal_catalog(portal_type="Project", id=project) # with id keyword, this function will return a sequence data type which contains one element.
project_object = project_list[0].getObject()

#    - Reference = automatically generated - already implemented
#    - Requester = current user person
#    - Start date = now
#    - State = submitted
#    - Billing Supplier = Project related Billing Supplier
#    - Location = Project related Location
#    - Supervisor = Project related Supervisor

support_request = portal.support_request_module.newContent(
  portal_type='Support Request',
  title=title,
  resource="service_module/" + resource,
  destination_decision_value=logged_in_user_value,
  source_decision_value = project_object.getSourceDecisionValue(),
  source_section_value = project_object.getSourceSectionValue(),
  source_project_value = project_object,
  destination_value = project_object.getDestinationValue(),
  start_date=now,
)

if description is not None or file is not None:
  portal.post_module.PostModule_createHTMLPostForSupportRequest(
    data="" if description is None else description,
    follow_up_value=support_request,
    # no predecessor
    file=file,
  )

support_request.submit()

return support_request.Base_redirect('officejs_support_request_view',
  keep_items={
    'portal_status_message': portal.Base_translateString(
      'New ${portal_type} created.',
      mapping={
        'portal_type': 'Support Request',
      },
    ),
  },
)
