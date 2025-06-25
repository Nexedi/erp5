from Products.CMFCore.utils import getToolByName

project = context
portal = project.getPortalObject()
domain_tool = getToolByName(portal, 'portal_domains')

if project.getPortalType() != "Project":
  return []

tmp_context = portal.discussion_thread_module.newContent(
  id='fake',
  portal_type='Discussion Thread',
  temp_object=True,
  follow_up=project.getRelativeUrl()
)

predicate_list = [x.getObject() for x in domain_tool.searchPredicateList(
  tmp_context,
  portal_type='Discussion Forum',
  tested_base_category_list=['follow_up']
)]

return predicate_list
