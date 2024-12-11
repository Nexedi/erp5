if not create_blog and not create_forum:
  return context.Base_redirect(
    form_id,
    keep_items = dict(portal_status_message = context.Base_translateString("Nothing to do."))
  )

membership_criterion_base_category_set = set(context.getMembershipCriterionBaseCategoryList())
multimembership_criterion_base_category_set = set(context.getMultimembershipCriterionBaseCategoryList())

multimembership_criterion_base_category_set.update(membership_criterion_base_category_set)
multimembership_criterion_base_category_set.add("publication_section")

membership_criterion_base_category_list = []
multimembership_criterion_base_category_list = list(multimembership_criterion_base_category_set)
membership_criterion_category_list = context.getMembershipCriterionCategoryList()

info_list = []

if create_blog:
  # create blog
  predicate = context.newContent(
    portal_type = 'Web Section', 
    id = blog_id,
    title = "Blog",
    visible = True,
    default_page_displayed = True,
    custom_render_method_id = "WebSection_viewBlogFrontPage",
    criterion_property = ("portal_type",),
    empty_criterion_valid = True,
    membership_criterion_base_category = membership_criterion_base_category_list,
    multimembership_criterion_base_category = multimembership_criterion_base_category_list,
    membership_criterion_category = membership_criterion_category_list + ["publication_section/blog"],
  )
  predicate.setCriterion("portal_type", "Web Page")
  info_list.append("blog")

if create_forum:
  # create forum
  predicate = context.newContent(
    portal_type = 'Web Section', 
    id = forum_id,
    title = "Forum",
    visible = True,
    default_page_displayed = True,
    authorization_forced = 1,
    custom_render_method_id = "WebSection_viewDiscussionThreadForm",
    criterion_property = ("portal_type",),
    empty_criterion_valid = True,
    membership_criterion_base_category = membership_criterion_base_category_list,
    multimembership_criterion_base_category = multimembership_criterion_base_category_list,
    membership_criterion_category = membership_criterion_category_list + ["publication_section/forum"],
  )
  predicate.setCriterion("portal_type", "Discussion Thread")
  info_list.append("forum")

info_list = info_list[:-2] + [" and ".join(info_list[-2:])]
info = ", ".join(info_list) + " created with default configuration."
info = info[:1].upper() + info[1:]
return context.Base_redirect(
  form_id,
  keep_items = dict(portal_status_message = context.Base_translateString(info))
)
