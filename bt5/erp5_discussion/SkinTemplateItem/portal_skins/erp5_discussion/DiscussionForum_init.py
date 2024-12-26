portal = context.getPortalObject()
type_definition = context.getTypeInfo()
membership_criterion_base_category_set = set([]) #set(context.getMembershipCriterionBaseCategoryList())
multimembership_criterion_base_category_set = set([]) #set(context.getMultimembershipCriterionBaseCategoryList())
multimembership_criterion_base_category_set.update(membership_criterion_base_category_set)
multimembership_criterion_base_category_set.add("publication_section")
membership_criterion_base_category_list = []
multimembership_criterion_base_category_list = list(multimembership_criterion_base_category_set)
membership_criterion_category_list = [] #context.getMembershipCriterionCategoryList()

context.setTitle("Forum")
context.edit(custom_render_method_id="WebSection_viewDiscussionThreadForm",
             default_page_displayed=True,
             criterion_property="portal_type",
             empty_criterion_valid=True,
             membership_criterion_base_category=membership_criterion_base_category_list,
             multimembership_criterion_base_category=multimembership_criterion_base_category_list,
             membership_criterion_category=membership_criterion_category_list + ["publication_section/forum"]) #???

# TODO FIX
#context.setCriterion("portal_type", "Discussion Thread")

# could / should use this pdm resource init?
'''
# from erp5_pdm/Resource_init.py
portal_type = context.getPortalType().lower().replace(' ', '_')

base = context.portal_preferences.getPreference('preferred_%s_variation_base_category_list' % portal_type, [])
optional = context.portal_preferences.getPreference('preferred_%s_optional_variation_base_category_list' % portal_type, [])
individual = context.portal_preferences.getPreference('preferred_%s_individual_variation_base_category_list' % portal_type, [])
use_list = context.portal_preferences.getPreference('preferred_%s_use_list' % portal_type, [])

context.edit(variation_base_category_list=base,
    optional_variation_base_category_list=optional,
    individual_variation_base_category_list=individual,
    use_list=use_list)
'''
