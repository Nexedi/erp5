import json
artifical_task = context
portal = artifical_task.getPortalObject()
current_user_value = portal.portal_membership.getAuthenticatedMember().getUserValue()

comment_list = []
for line in artifical_task.objectValues(
  portal_type='Artificial Task Line',
  sort_on=[('creation_date', 'ascending')],
  simulation_state = ('stopped', 'delivered')
 ):
  report_line = line.getFollowUpRelatedValue(portal_type='Artificial Task Report Line')
  if report_line:
    report_message_list = json.loads(report_line.getTextContent())
    tool_message_list = [x for x in report_message_list if x.get('role', '') in ('tool', 'assistant')]
  else:
    tool_message_list = []

  author_value = line.getSourceValue()
  is_own_comment = (
    author_value is not None
    and current_user_value is not None
    and author_value.getRelativeUrl() == current_user_value.getRelativeUrl()
  )

  comment_list.append((dict(
    date=line.getCreationDate().ISO8601(),
    text=line.getTextContent(),
    tool_message_list = json.dumps(tool_message_list),
    response = not is_own_comment,
    author_title = author_value.getTitle() if author_value else '',
    author_url = author_value.getRelativeUrl() if author_value else ''
  )))

return comment_list
