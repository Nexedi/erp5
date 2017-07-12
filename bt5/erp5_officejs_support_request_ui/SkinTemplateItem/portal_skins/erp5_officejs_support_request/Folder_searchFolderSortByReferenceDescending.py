if 'sort_on' in kw:
  del kw['sort_on']

return context.searchFolder(sort_on=[('modification_date', 'descending')], **kw)
