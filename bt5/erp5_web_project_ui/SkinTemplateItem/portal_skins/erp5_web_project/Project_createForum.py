project = context
forum = None

# check if project already has a forum
follow_up_list = [x for x in project.getFollowUpRelatedValueList(portal_type = "Discussion Forum") if x.getValidationState()
                  in ('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive')]
if len(follow_up_list) > 0:
  forum = follow_up_list[0]
if not forum:
  predicate_list = project.Project_getForumPredicateList()
  if len(predicate_list) > 0:
    forum = context.restrictedTraverse(predicate_list[0])

if forum:
  return project.Base_redirect(
    'view',
    keep_items = dict(portal_status_message = context.Base_translateString("The project already has a valid forum: " + forum.getRelativeUrl()))
  )

membership_criterion_base_category_list = []
multimembership_criterion_base_category_list = ["publication_section"]
membership_criterion_category_list = ['publication_section/forum']

'''
# TODO: create sub default web site and forum web section?
sub_web_section = context.newContent(
  portal_type = 'Web Section',
  id = forum_id,
  title = "Forum",
  visible = True,
  default_page_displayed = True,
  authorization_forced = 1,
  custom_render_method_id = "WebSection_viewDiscussionThreadForm",
  empty_criterion_valid = True
)'''
# create forum
portal = context.getPortalObject()
module =  portal.getDefaultModule("Discussion Forum")
forum = module.newContent(portal_type="Discussion Forum")
forum.setMultimembershipCriterionBaseCategoryList(multimembership_criterion_base_category_list)
forum.setMembershipCriterionCategoryList(membership_criterion_category_list)
forum.edit(criterion_property=("portal_type",))
forum.setCriterion("portal_type", ["Discussion Thread"])
#TODO: if a default web section is created, add it to forum follow up list (for backward compatibility)
forum.setFollowUp(project.getRelativeUrl())

return forum.Base_redirect(
  'Predicate_view',
  keep_items = dict(portal_status_message = context.Base_translateString("New forum created. Please validate the forum and finish to set Predicate configuration."))
)
