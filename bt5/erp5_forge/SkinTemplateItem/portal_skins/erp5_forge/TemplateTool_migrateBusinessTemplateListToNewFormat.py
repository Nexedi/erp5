if not repository_list:
  return context.Base_redirect(keep_items={'portal_status_message': 'No '+
       'repository was defined'})
context.portal_templates.importAndReExportBusinessTemplateListFromPath(repository_list)
return context.Base_redirect(keep_items={'portal_status_message': 'Migration '+
       'started, please check your portal activities'})
