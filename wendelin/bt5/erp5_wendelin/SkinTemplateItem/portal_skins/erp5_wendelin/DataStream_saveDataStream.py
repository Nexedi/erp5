request = container.REQUEST
response =  request.response

field_prefix = 'field_my_' # Prevent changing the prefix through publisher
field_prefix_len = len(field_prefix)
fields = {}

for key, value in request.form.items():
  if key.startswith(field_prefix) and value:
    fields[key[field_prefix_len:]] = value

if fields.has_key('append_file'):
  context.appendData(fields['append_file'].read())
  del fields['append_file']

context.edit(**fields)
message = context.Base_translateString("Data Stream updated")
return context.Base_redirect(
  'view', 
  keep_items=dict(portal_status_message=message), 
  **kw
)
