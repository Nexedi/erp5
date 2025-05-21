category_list = context.getMembershipCriterionCategoryList()
context.setCategoryList(category_list)
context.Base_redirect('view',keep_items={'portal_status_message': 'Discussion Forum categories updated.'})
