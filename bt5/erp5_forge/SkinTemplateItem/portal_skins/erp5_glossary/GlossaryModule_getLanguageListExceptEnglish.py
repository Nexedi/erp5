return [(label, value)
        for label, value in context.portal_categories.language.getCategoryChildCompactLogicalPathItemList(local_sort_id="int_index")
        if value!='en']
