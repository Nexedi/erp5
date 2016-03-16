"""
  This script provides all required details of an ERP5 form + values
  on respective context. Using these values a javascript client can construct
  form at client side.
"""
from json import dumps

LIST_FIELDS = ["ListField", "ParallelListField"]

MARKER = ['', None]
result = {'form_data': {}, }

# use form_id to get list of keys we care for
form = getattr(context, form_id)
for field_id in form.get_field_ids():
  base_field_id = field_id.replace("my_", "")
  field = getattr(form, field_id)
  original_field = field
  if field.meta_type == "ProxyField":
    field = field.getRecursiveTemplateField()
  field_meta_type = field.meta_type
  field_value = original_field.get_value("default")
  field_dict = result['form_data'][field_id] = {}

  field_dict['type'] = field_meta_type
  field_dict['editable'] = original_field.get_value("editable")
  field_dict['css_class'] = original_field.get_value("css_class")
  field_dict['hidden'] = original_field.get_value("hidden")
  field_dict['description'] = original_field.get_value("description")
  field_dict['enabled'] = original_field.get_value("enabled")
  field_dict['title'] = original_field.get_value("title")
  field_dict['required'] = original_field.is_required()
  field_dict['alternate_name'] = original_field.get_value("alternate_name")
  # XXX: some fields have display_width some not (improve)
  try:
    field_dict['display_width'] = original_field.get_value("display_width")
  except:
    field_dict['display_width'] = None

  if field_meta_type in ["DateTimeField"]:
    if field_value not in MARKER:
      field_value = field_value.millis()
      field_dict['format'] = context.portal_preferences.getPreferredDateOrder('ymd')

  # listbox
  if field_meta_type in ["ListBox"]:
    field_dict['listbox'] = {}
    if render_client_side_listbox:
      # client side can request its javascript representation so it can generate it using jqgrid
      # or ask server generate its entire HTML
      field_dict['type'] = 'ListBoxJavaScript'
      field_dict['listbox']['lines'] = original_field.get_value("lines")
      field_dict['listbox']['columns'] = [x for x in original_field.get_value("columns")]
      field_dict['listbox']['listbox_data_url'] = "Listbox_asJSON"
    else:
      # server generates entire HTML
      field_dict['listbox']['listbox_html'] = original_field.render()

  if field_meta_type in LIST_FIELDS:
    # form contains selects, pass list of selects' values and calculate default one?
    field_dict['items'] = original_field.get_value("items")

  if field_meta_type in ["FormBox"]:
    # this is a special case as this field is part of another form's fields
    formbox_target_id = original_field.get_value("formbox_target_id")
    formbox_form = getattr(context, formbox_target_id)
    # get all values
    for formbox_field_id in formbox_form.get_field_ids():
      formbox_field_id_field = getattr(formbox_form, formbox_field_id)
      field_value = formbox_field_id_field.get_value("default") # only last wins ?

  # add field value
  field_dict['value'] =  field_value

return dumps(result)
