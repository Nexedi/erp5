context.log("[DEBUG] create forum!")
a = [context.log(k) for k, val in kw.items()]
a = [context.log(val) for k, val in kw.items()]
'''dialog_id DiscussionForumModule_viewNewForumDialog
dialog_method DiscussionForumModule_createNewForum
field_your_title [title input]
title [title input]
selection_name discussion_forum_module_selection
keep_items {}
field_your_predecessor
form_id DiscussionForumModule_viewDiscussionForumList'''

''' #if there is a related obj (document, site, project):
membership_criterion_base_category_set = set(context.getMembershipCriterionBaseCategoryList())
multimembership_criterion_base_category_set = set(context.getMultimembershipCriterionBaseCategoryList())

multimembership_criterion_base_category_set.update(membership_criterion_base_category_set)
multimembership_criterion_base_category_set.add("publication_section")

membership_criterion_base_category_list = []
multimembership_criterion_base_category_list = list(multimembership_criterion_base_category_set)
membership_criterion_category_list = context.getMembershipCriterionCategoryList()
'''

category_list = []
membership_criterion_base_category_list = []
membership_criterion_category_list = [] #['publication_section/forum'] #or related_doc.getMembershipCriterionCategoryList()
multimembership_criterion_base_category_set = set(context.getMultimembershipCriterionBaseCategoryList())
multimembership_criterion_base_category_set.add("publication_section")
multimembership_criterion_base_category_list = list(multimembership_criterion_base_category_set)
#multimembership_criterion_base_category_list = ['publication_section'] # or related_doc.getMultimembershipCriterionBaseCategoryList()
for base_category in multimembership_criterion_base_category_list:
  category_list.extend([x for x in membership_criterion_category_list if x.startswith(base_category)])

context.log("[DEBUG] creating FORUM with params:")
context.log("membership_criterion_base_category")
context.log(membership_criterion_base_category_list)
context.log("multimembership_criterion_base_category")
context.log(multimembership_criterion_base_category_list)
context.log("membership_criterion_category")
context.log(membership_criterion_category_list + ["publication_section/forum"])
context.log("and category list:")
context.log(category_list)

predicate = context.newContent(
  portal_type = 'Discussion Forum',
  title = title,
  criterion_property = ("portal_type",),
  empty_criterion_valid = True,
  membership_criterion_base_category = membership_criterion_base_category_list,
  multimembership_criterion_base_category = multimembership_criterion_base_category_list,
  membership_criterion_category = membership_criterion_category_list + ["publication_section/forum"],
)
predicate.setCriterion("portal_type", "Discussion Thread")
predicate.setCategoryList(category_list)

return context.Base_redirect(
  predicate.getAbsoluteUrl(),
  keep_items = dict(portal_status_message = context.Base_translateString("New discussion forum created."))
)
