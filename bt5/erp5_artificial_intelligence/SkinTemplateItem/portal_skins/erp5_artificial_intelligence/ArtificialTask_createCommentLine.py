import json
artificial_task = context
portal = artificial_task.getPortalObject()

line = artificial_task.newContent(portal_type='Artificial Task Line', text_content=data)
line.setSourceValue(portal.portal_membership.getAuthenticatedMember().getUserValue())
line.stop()

return json.dumps({
  "post": {
    "date": line.getCreationDate().ISO8601(),
    "text": data,
    "response": False
  }
})
