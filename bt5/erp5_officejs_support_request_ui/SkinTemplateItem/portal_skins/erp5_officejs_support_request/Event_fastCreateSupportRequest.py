portal = context.getPortalObject()
module = portal.support_request_module
request = container.REQUEST
logged_in_user_value = portal.portal_membership.getAuthenticatedMember().getUserValue()
now = DateTime()

# FIXME: What is the Support Request Type????

# default_field_your_resource,field_your_title, field_your_project, default_field_your_project, form_id, field_your_resource, dialog_id, title, project, resource, dialog_method
project_list = portal.portal_catalog(portal_type="Project", id=project) # with id keyword, this function will return a sequence data type which contains one element.
project_object = project_list[0].getObject()
# raise NotImplementedError(project_object.getTitle())
# .getTitle())

# Create a new object
# project_list = portal.portal_catalog(portal_type="Project")
# project = project_list[0].getObject()
# project_title = project.getTitle()
# organisation_list = portal.portal_catalog(portal_type="Organisation")
# organisation = organisation_list[1]
# who1 = project_object.getSourceDecisionValue() # Supervisor
# org = project_object.getSourceSectionValue() # Billing supplier, this is an Organisation
# org = source_section_relative_url
# who = project.source_decision_relative_url
# org = project.getOrganisationModule()
# organisation_module = context.getOrganisationModule()

# project.getSupervisor() ??
# project_billing_supplier = project.get
# raise NotImplementedError(org.getTitle())

support_request = portal.support_request_module.newContent(
  portal_type='Support Request',
  title=title,
  resource=resource,
)
# event_portal_type = module.getReference()
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
  start_date=now,
)

support_request.submit()

return support_request.Base_redirect('fast_view',
  keep_items={
    'portal_status_message': portal.Base_translateString(
      'New ${portal_type} created.',
      mapping={
        'portal_type': 'Support Request',
      },
    ),
  },
)
