portal = context.getPortalObject()
logged_in_user_value = portal.portal_membership.getAuthenticatedMember().getUserValue()

now = DateTime()

# default_field_your_resource,field_your_title, description, field_your_project, default_field_your_project, form_id, field_your_resource, dialog_id, resource, title, file, project, dialog_method, field_my_description, field_your_file=None
project_list = portal.portal_catalog(portal_type="Project", id=project) # with id keyword, this function will return a sequence data type which contains one element.
project_object = project_list[0].getObject()

support_request = portal.support_request_module.newContent(
  portal_type='Support Request',
  title=title,
  resource="service_module/" + resource,
)

# support_request.Base_getRelatedPostList

#    - Reference = automatically generated - already implemented
#    - Requester = current user person
#    - Start date = now
#    - State = submitted
#    - Billing Supplier = Project related Billing Supplier
#    - Location = Project related Location
#    - Supervisor = Project related Supervisor

support_request.edit(
  destination_decision_value=logged_in_user_value,
  source_decision_value = project_object.getSourceDecisionValue(),
  source_section_value = project_object.getSourceSectionValue(),
  source_project_value = project_object,
  destination_value = project_object.getDestinationValue(),
  start_date=now,
)


support_request.submit()
support_request.immediateReindexObject()

if description is not None or file is not None:
  portal.post_module.PostModule_createHTMLPostForSupportRequest(
    follow_up=support_request.getRelativeUrl(),  # XXX give support_request as follow_up_value
    predecessor=None,
    data="" if description is None else description,
    file=file,
  )

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
