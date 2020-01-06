'''Returns all possible document conversions from the `base_content_type`.
'''
td = context.getPortalObject().portal_trash.newContent(
    portal_type='OOo Document',
    temp_object=True,
    base_content_type=base_content_type,
    base_data='not empty')
return  [('', '')] + td.getTargetFormatItemList()
