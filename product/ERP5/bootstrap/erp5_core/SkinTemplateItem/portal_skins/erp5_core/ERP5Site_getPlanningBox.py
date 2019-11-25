# Return first listbox in a form that is enabled and not hidden
# Christophe Dumez <christophe@nexedi.com>
# This script should be used to detect a listbox without having to name it "listbox"

if form is None:
  form=context

if form.meta_type != 'ERP5 Form':
  return None

# we start with 'bottom' because most of the time
# the listbox is there.
for group in ('bottom', 'center', 'left', 'right'):
  for field in form.get_fields_in_group(group):
    if field.meta_type == 'PlanningBox' and not(field['hidden']) and field['enabled']:
      return field
