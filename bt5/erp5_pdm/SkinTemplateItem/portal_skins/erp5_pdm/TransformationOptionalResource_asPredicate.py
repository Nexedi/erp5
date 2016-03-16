option_category = context.getOptionList()
option_base_category = []
if len(option_category) > 0:
  option_base_category = [option_category[0].split('/')[0]]

new_context = context.asContext(
    membership_criterion_category=option_category,
    membership_criterion_base_category=option_base_category)
return new_context
