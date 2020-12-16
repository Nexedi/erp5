# Return first listbox in a form that is enabled and not hidden
# This script should be used to detect a listbox without having to name it "listbox"

form=context

if form.meta_type != 'ERP5 Form':
  return None

# XXX We should not use meta_type properly,
# XXX We need to discuss this problem.(yusei)
def isListBox(field):
  if field.meta_type=='ListBox':
    return True
  elif field.meta_type=='ProxyField':
    template_field = field.getRecursiveTemplateField()
    if template_field.meta_type=='ListBox':
      return True
  return False

# we start with 'bottom' because most of the time
# the listbox is there.
for group in ('bottom', 'center', 'left', 'right', 'Default'):
  for field in form.get_fields_in_group(group):
    if isListBox(field) and not(field['hidden']) and field['enabled']:
      return field
