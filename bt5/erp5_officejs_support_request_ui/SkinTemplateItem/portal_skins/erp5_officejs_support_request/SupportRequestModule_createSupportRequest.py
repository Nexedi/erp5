# pylint:disable=redefined-builtin
# this script uses file= argument
portal = context.getPortalObject()
translateString = portal.Base_translateString
logged_in_user_value = portal.portal_membership.getAuthenticatedMember().getUserValue()

now = DateTime()

project_object = portal.project_module[project]

support_request = portal.support_request_module.newContent(
  portal_type='Support Request',
  title=title,
  resource=resource,
  destination_decision_value=logged_in_user_value,
  source_decision_value = project_object.getSourceDecisionValue(),
  source_section_value = project_object.getSourceSectionValue(),
  source_project_value = project_object,
  destination_value = project_object.getDestinationValue(),
  destination_section_value = project_object.getDestinationSectionValue(),
  start_date=now,
)

support_request.submit()

if description is not None or file is not None:
  portal.post_module.PostModule_createHTMLPostForSupportRequest(
    follow_up=support_request.getRelativeUrl(),  # XXX give support_request as follow_up_value
    predecessor=None,
    data="" if description is None else description,
    file=file,
    web_site_relative_url=context.getWebSiteValue().getRelativeUrl(),
    source_reference=source_reference,
  )

return support_request.Base_redirect('officejs_support_request_view',
  keep_items={
    'portal_status_message': translateString(
      'New Support Request created.',
      default=translateString(
          "New ${portal_type} created.",
          mapping={"portal_type": translateString("Support Request")}),
    ),
  },
)
