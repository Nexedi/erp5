# XXX the name of this script is bad as the context is not a predicate

category_list = request.get('field_my_membership_criterion_base_category_list', [])
if not same_type(category_list, []):
  category_list = [category_list]
multimembership_criterion_base_category_list = request.get('field_my_multimembership_criterion_base_category_list', [])
if not same_type(multimembership_criterion_base_category_list, []):
  multimembership_criterion_base_category_list = [multimembership_criterion_base_category_list]
category_list += [i for i in multimembership_criterion_base_category_list \
                  if i not in category_list]
portal_categories = context.getPortalObject().portal_categories

for item in item_list:
  base_category, relative_url = item.split('/', 1)
  if base_category not in category_list or \
      portal_categories.restrictedTraverse(relative_url, None) is None:
    return 0
return 1
