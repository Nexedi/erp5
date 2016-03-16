kw.update(context.REQUEST.form)
# Clear selection
context.portal_selections.setSelectionCheckedUidsFor('template_tool_install_selection', [])
# Then call the listbox
kw.update(context.REQUEST.form)
return context.ERP5Site_redirect("%s/%s" % (context.absolute_url(), 'TemplateTool_viewInstallRepositoryBusinessTemplateListDialog'), keep_items={'dialog_category': dialog_category, 'form_id': form_id, 'cancel_url': cancel_url}, **kw)
