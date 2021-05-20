import json
data_dict = json.loads(text_content)
portal_type = data_dict["portal_type"]
module = context.getPortalObject().getDefaultModule(portal_type)
document = module.newContent(
  portal_type=portal_type,
  text_content=text_content,
)
return json.dumps({
  "id": document.getRelativeUrl()
})
