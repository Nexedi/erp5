template_list = [x.getTitle() for x in context.portal_templates.getInstalledBusinessTemplateList()]
template_list.sort()
return template_list
