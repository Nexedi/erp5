context.setTitle("New Forum")
context.edit(criterion_property=("portal_type",),
             empty_criterion_valid=True,
             membership_criterion_base_category=[],
             multimembership_criterion_base_category=["publication_section"],
             membership_criterion_category= ["publication_section/forum"])
context.setCriterion("portal_type", "Discussion Thread")
