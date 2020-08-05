project_uid_list = [x.uid for x in context.portal_catalog(
     relative_url='%s/%%' % context.getRelativeUrl())] + [context.getUid()]

kw['related_source_project_or_destination_project'] = project_uid_list
return context.portal_catalog(**kw)
