"""
  Get search text from REQUEST or selection.
"""
if argument_name_list is None:
  argument_name_list = []

request = context.REQUEST

if not argument_name_list:
  form_id = request.get('listbox_form_id', None)
  field_id = request.get('listbox_field_id', None)
  if form_id is not None and field_id is not None:
    # get values from current ERP5 form listbox being rendered
    form = getattr(context, form_id)
    field = getattr(form, field_id)
    global_search_column = field.get_value('global_search_column')
    argument_name_list = (global_search_column,)
  else:
    # get search words from listbox selection using hard coded default fields
    argument_name_list = ('advanced_search_text', 'title', 'reference', \
                          'SearchableText', 'searchabletext', \
                          'searchabletext_any', 'searchabletext_all', \
                          'searchabletext_phrase',)

if selection is None:
  selection_name = request.get("selection_name", None)
  if selection_name is not None:
    selection = context.portal_selections.getSelectionFor(selection_name)

params = {}
if selection is not None:
  params = selection.getParams()

params = [request.get(name, params.get(name, '')) for name in argument_name_list]
# flatten value if it is list
params = [(hasattr(param, 'sort') and ' '.join(param) or param) for param in params]
search_string = ' '.join(params).strip()

return search_string
