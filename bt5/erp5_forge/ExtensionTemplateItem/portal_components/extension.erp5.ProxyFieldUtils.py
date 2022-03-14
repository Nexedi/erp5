### External Method

from Products.Formulator.MethodField import Method

#
# This function is useful to check if two fields is equal or not.
#
def get_field_data(field):
  value_dict = {}
  tales_dict = {}

  if field.meta_type=='ProxyField':
    template_field = field.getRecursiveTemplateField()
    for ui_field_id in list(template_field.form.fields.keys()):
      value = field.get_recursive_orig_value(ui_field_id)
      if isinstance(value, Method):
        value = value.method_name
      tales = field.get_recursive_tales(ui_field_id)
      if tales:
        tales_text = tales._text
      else:
        tales_text = ''
      value_dict[ui_field_id] = value
      tales_dict[ui_field_id] = tales_text
  else:
    for ui_field_id in list(field.form.fields.keys()):
      value = field.get_orig_value(ui_field_id)
      if isinstance(value, Method):
        value = value.method_name
      tales = field.get_tales(ui_field_id)
      if tales:
        tales_text = tales._text
      else:
        tales_text = ''
      value_dict[ui_field_id] = value
      tales_dict[ui_field_id] = tales_text

  return value_dict, tales_dict
