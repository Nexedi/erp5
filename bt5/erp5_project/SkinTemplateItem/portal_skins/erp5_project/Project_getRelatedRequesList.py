project_uid_list = [x.uid for x in context.portal_catalog(
     relative_url='%s/%%' % context.getRelativeUrl())] + [context.getUid()]

return context.portal_catalog(
                                                         selection_report=selection_report,
                                                         portal_type=portal_type,
            related_source_project_or_destination_project = project_uid_list )
