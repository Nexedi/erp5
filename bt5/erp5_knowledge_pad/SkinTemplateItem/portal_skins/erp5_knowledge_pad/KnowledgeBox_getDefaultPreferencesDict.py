box = context
preferences = {}

# get default properties from Gadget only if edit form is available
gadget = box.getSpecialiseValue()
edit_form_id = gadget.getEditFormId()

if edit_form_id is not None:
  edit_form = getattr(context, edit_form_id, None)
  if edit_form is not None:
    fields = [x for x in edit_form.objectValues() if x.getId().startswith('my_')]
    for field in fields:
      field_id = field.getId().replace('my_', '')
      # box has higher priority so check it first
      field_value = getattr(box, field_id, getattr(gadget, field_id, None))
      if(field.meta_type.startswith('Multi') and not same_type(field_value, []) and not same_type(field_value, ()) and field_value != None):
        preferences[field_id] = [field_value]
      else:
        preferences[field_id] = field_value
return preferences
