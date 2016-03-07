categories_list = context.getCategoriesList()
categories_list.sort(key=lambda x: x.split("/", 1)[0])
return categories_list
