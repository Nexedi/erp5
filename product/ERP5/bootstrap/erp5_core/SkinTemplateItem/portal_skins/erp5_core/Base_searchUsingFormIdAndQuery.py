"""Return an Iterator over database result from `form_id`'s listbox and optional `query`.

This script is intended to be used only internally.
"""

form = getattr(context, form_id)
listbox = form.Form_getListbox()

return context.Base_searchUsingListbox(listbox, query, sort_on, limit)
