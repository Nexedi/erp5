template_tool = context.portal_templates

matching = []

for o in template_tool.contentValues(portal_type='Business Template'):
  if portal_type in o.getTemplatePortalTypeIdList():
    matching.append(o.getUid())
  else:
    allowed_content_type_list = o.getTemplatePortalTypeAllowedContentTypeList()
    allowed_content_type_list = map(lambda x: x and x.split('|')[1].strip(), allowed_content_type_list)
    if portal_type in allowed_content_type_list:
      matching.append(o.getUid())

for o in template_tool.contentValues(portal_type='Business Template'):
  if portal_type in o.getTemplatePortalTypeIdList():
    matching.append(o.getUid())

return template_tool.Base_redirect('TemplateTool_viewBusinessTemplateList', keep_items=dict(uid=matching, reset=1))
