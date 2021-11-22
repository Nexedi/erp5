"""This is the action for the Base_viewPrintDialog.
"""
# prevent lose checked itens after click to print
context.Base_updateListboxSelection()

if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 150)

if print_mode == 'list_view':
  return context.Folder_viewContentListReport()

return getattr(context, form_id)()
