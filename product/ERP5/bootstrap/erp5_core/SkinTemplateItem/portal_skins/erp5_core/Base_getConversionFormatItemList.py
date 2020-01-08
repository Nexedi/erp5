'''Returns all possible document conversions from the `base_content_type`.
'''
td = context.newContent(
    portal_type='OOo Document',
    temp_object=True,
    base_content_type=base_content_type,
    base_data='not empty')
return  [('', '')] + td.getTargetFormatItemList()
