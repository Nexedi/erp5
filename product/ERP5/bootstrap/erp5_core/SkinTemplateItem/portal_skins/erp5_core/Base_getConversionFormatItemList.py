"""
Returns all possible document conversions from the `content_type`.
"""
# Compatibility: we previously used `base_content_type`
if "base_content_type" in kw and not content_type:
  content_type = kw["base_content_type"]

td = context.newContent(
    portal_type='OOo Document',
    temp_object=True,
    content_type=content_type,
    data=b'not empty')

return  [('', '')] + sorted(td.getTargetFormatItemList())
