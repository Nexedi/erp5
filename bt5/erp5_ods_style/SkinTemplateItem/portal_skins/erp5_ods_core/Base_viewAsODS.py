context.getPortalObject().portal_skins.changeSkin('ODS')
request = container.REQUEST
request.set('portal_skin', 'ODS') # Some TALES expressions checks this

if target_language:
  request['AcceptLanguage'].set(target_language, 150)

if print_mode == 'list_view' or print_mode == 'list_view_separate_sheet':
  if print_mode == 'list_view_separate_sheet':
    request.set('sheet_per_report_section', 1)
  return context.Folder_viewContentListAsODSReport()

return getattr(context, form_id)()
