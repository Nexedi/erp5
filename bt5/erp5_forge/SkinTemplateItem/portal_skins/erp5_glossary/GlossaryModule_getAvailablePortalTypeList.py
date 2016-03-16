portal_type_list = [x for x in context.portal_types.objectIds() \
                    if not x.endswith(' Module')]
portal_type_list.sort()
return portal_type_list
