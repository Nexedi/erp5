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
  publication_section='forum',
  follow_up=project.getRelativeUrl()
)

def filter_method(element_list):
  return [x for x in element_list if 'follow_up' in x.getMultimembershipCriterionBaseCategoryList()]

predicate_list = [x.getObject() for x in domain_tool.searchPredicateList(
  tmp_context,
  portal_type='Discussion Forum',
  filter_method=filter_method,
  tested_base_category_list=['follow_up']
)]

return predicate_list
