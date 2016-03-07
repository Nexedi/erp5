# return the list of business_template, optionnally filtered by title, for installation dialog.
template_list = context.getRepositoryBusinessTemplateList(**kw)

# XXX this is not usual catalog syntax ...
title = title.replace('%', '')

if title:
  return [bt for bt in template_list if title in bt.getTitle()]

return template_list
