from Products.CMFCore.utils import getToolByName

project = context
portal = project.getPortalObject()
domain_tool = getToolByName(portal, 'portal_domains')

tested_base_category_list = ['follow_up']
# not used, as thread-project is a follow_up relation
destination_value = portal.portal_membership.getAuthenticatedMember().getUserValue()
#predicate_portal_type = 'Project'
predicate_portal_type = 'Web Section' #after migration this will be 'Discussion Forum'

#e.g.
#MultimembershipCriterionBaseCategoryList:
#['follow_up', 'publication_section']
#MembershipCriterionCategoryList:
#['publication_section/forum', 'follow_up/project_module/20120914-11FAD6']

tmp_forum = portal.portal_trash.newContent(
  portal_type='Web Section',
  temp_object=1,
  multimembership_criterion_base_category_list=['follow_up', 'publication_section'],
  multimembership_criterion_category_list=['publication_section/forum', 'follow_up/' + project.getRelativeUrl()],
  follow_up=project.getRelativeUrl()
)

tmp_context = portal.portal_trash.newContent(
  portal_type='Discussion Thread',
  temp_object=1,
  predecessor=tmp_forum.getRelativeUrl(),
  follow_up=project.getRelativeUrl()
)
print("tmp_context", tmp_context)
# e.g. discussion_thread_module/278/getFollowUpList : project_module/20120914-11FAD6

predicate_list = [x.getObject() for x in domain_tool.searchPredicateList(
  tmp_context,
  portal_type=predicate_portal_type,
  acquired=0,
  tested_base_category_list=tested_base_category_list
)]
print("predicate_list", predicate_list)
return printed
return predicate_list
