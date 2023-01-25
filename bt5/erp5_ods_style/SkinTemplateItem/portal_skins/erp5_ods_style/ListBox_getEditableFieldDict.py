request = container.REQUEST

# XXX this is a restricted environment available reimplementation of ListboxRenderer.getEditableField
editable_columns = set(tuple(context.get_value('columns', REQUEST=request))
  + tuple(context.get_value('all_columns', REQUEST=request)))

editable_fields = {}

def getEditableField(alias):
  """Get an editable field for column, using column alias.
  Return None if a field for this column does not exist.
  """
  field = context
  original_field_id = field.id
  while True:
    for field_id in {original_field_id, field.id}:
      if field.aq_parent.has_field("%s_%s" % (field_id, alias), include_disabled=1):
        return field.aq_parent.get_field("%s_%s" % (field_id, alias),
                                         include_disabled=1)
    if field.meta_type != 'ProxyField':
      return None
    # if we are rendering a proxy field, also look for editable fields from
    # the template field's form. This editable field can be prefixed either
    # by the template field listbox id or by the proxy field listbox id.
    field = field.getTemplateField().aq_inner

for column, _ in editable_columns:
  field = getEditableField(column)
  if field is not None:
    editable_fields[column] = field

return editable_fields
