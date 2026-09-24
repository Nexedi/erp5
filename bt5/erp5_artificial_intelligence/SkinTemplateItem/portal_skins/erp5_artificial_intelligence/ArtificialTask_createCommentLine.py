import json
artificial_task = context
portal = artificial_task.getPortalObject()

line = artificial_task.newContent(portal_type='Artificial Task Line', text_content=data)
author = portal.portal_membership.getAuthenticatedMember().getUserValue()
line.setSourceValue(author)

line.deliver()

if len(artificial_task.getContributorList(portal_type='Person')) <= 1:
  artificial_task.restart()

return json.dumps({
  "post": {
    "date": line.getCreationDate().ISO8601(),
    "text": data,
    "response": False
  }
})
