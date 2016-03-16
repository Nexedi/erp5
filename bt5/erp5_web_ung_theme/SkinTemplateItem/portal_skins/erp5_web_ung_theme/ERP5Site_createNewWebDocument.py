from zExceptions import Unauthorized

if context.portal_membership.isAnonymousUser():
  raise Unauthorized("You are not allowed to use this script")

request = context.REQUEST
template_name = template or request.get("template")
if template_name is None:
  return None

template_relative_url = "portal_preferences/ung_preference/%s" % template_name
# Create the new content in appropriate module
portal = context.getPortalObject()
template = portal.restrictedTraverse(template_relative_url)
preference = template.getParentValue()

preference.manage_copyObjects(ids=[template.getId()], REQUEST=request, RESPONSE=None)
new_content_list = portal.web_page_module.manage_pasteObjects(request['__cp'])
new_content_id = new_content_list[0]['new_id']
new_content = portal.web_page_module[new_content_id]
new_content.makeTemplateInstance()

portal_type = new_content.getPortalType()
module = portal.getDefaultModule(portal_type)

kw["webpage_path"] = new_content.getPath()
return new_content.Base_redirect(keep_items = dict(editable_mode=1, **kw))
