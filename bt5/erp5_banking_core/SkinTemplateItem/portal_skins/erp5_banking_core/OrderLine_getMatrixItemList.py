my_category_list =[]
for y in base_category_list :
    my_category_list += [x[1] for x in context.portal_categories[y].getCategoryChildTitleItemList(base=1)[1:]]
return my_category_list
