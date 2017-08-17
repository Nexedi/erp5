if 'sort_on' in kw:
  del kw['sort_on']

# raise NotImplementedError(kw)

return context.searchFolder(sort_on=[('modification_date', 'descending')], **kw)
