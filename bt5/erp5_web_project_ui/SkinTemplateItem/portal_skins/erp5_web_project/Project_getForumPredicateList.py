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

predicate_list = [x.getRelativeUrl() for x in domain_tool.searchPredicateList(
  tmp_context,
  portal_type='Discussion Forum',
  validation_state=('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive'),
  filter_method=filter_method,
  tested_base_category_list=['follow_up']
)]

follow_up_list = [x.getRelativeUrl() for x in project.getFollowUpRelatedValueList(portal_type = "Discussion Forum") if x.getValidationState()
                  in ('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive')]

return list(set(predicate_list + follow_up_list))
