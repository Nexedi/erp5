listbox = getattr(context, context.REQUEST.form_id, None).get_field( context.REQUEST.field_id )
dialog_id = listbox.get_value('relation_form_id') or 'Base_viewRelatedObjectList'
result = listbox.get_value('columns')

if result in [ [], (), None, '']:
  result = getattr(context, dialog_id, None).get_field( 'listbox' ).get_value('columns')

return result
