"""Extract search settings from a listbox and issue search using `query`.

Listbox is a search-capable component but searching using it is not straightforward. This
script solves exactly that.

Returns an iterable (most likely SearchResult instance depending on list_method definition)
"""

list_method_kwargs = dict(listbox.get_value('default_params')) or {}

# Listbox contraints portal types
portal_types = listbox.get_value('portal_types')
if portal_types:
  if "portal_type" in list_method_kwargs:
    if isinstance(list_method_kwargs['portal_type'], (str, unicode)):
      list_method_kwargs['portal_type'] = [list_method_kwargs['portal_type'], ]
  else:
    list_method_kwargs['portal_type'] = []
  list_method_kwargs['portal_type'].extend(portal_type_name for portal_type_name, _ in portal_types)

# query is provided by the caller because it is a runtime information
if query:
  list_method_kwargs.update(full_text=query) # second overwrite the query

list_method_name = listbox.get_value('list_method').getMethodName()
list_method = getattr(context, list_method_name)  # get the list_method with correct context

return list_method(**list_method_kwargs)
