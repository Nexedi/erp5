def edit(url, edit_order, cleaned_v):
  context.setTranslationDomain(url.split("/")[-1], cleaned_v['domain_name'])
return context.Base_edit(form_id, listbox_edit=edit, *args, **kw)
