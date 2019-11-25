"""Return first listbox in a form that is enabled and not hidden

This script should be used to detect a listbox without having to name it "listbox".

:param form_or_id: {Form/str} optional Form instance (otherwise context-Form) or form_id (will be retrieved on context-Document)

Christophe Dumez <christophe@nexedi.com>
"""
from Products.ERP5Type.Log import log, ERROR

def isListBox(field):
  if field.meta_type == "ListBox":
    return True
  elif field.meta_type == "ProxyField":
    template_field = field.getRecursiveTemplateField()
    if template_field.meta_type == "ListBox":
      return True
  return False

if form_or_id is None:
  form = context
elif isinstance(form_or_id, str):
  try:
    form = getattr(context, form_or_id)
  except AttributeError:
    log("Form '{}' does not exist!", level=ERROR)
    return None
else:
  form = form_or_id

if form.meta_type not in ('ERP5 Form', 'Folder', 'ERP5 Folder'):
  raise RuntimeError("Cannot get Listbox field from \"{!s}\"! Supported is only ERP5 Form and (ERP5) Folder".format(form.meta_type))

listbox = None

if "Form" in form.meta_type and form.has_field("listbox"):
  listbox = form.get_field("listbox")
elif "Folder" in form.meta_type:
  listbox = getattr(form, "listbox", None)

if listbox:
  return listbox

# we start with 'bottom' because most of the time
# the listbox is there.
for group in ('bottom', 'center', 'left', 'right'):
  for field in form.get_fields_in_group(group):
    if (isListBox(field) and
        not field.get_value('hidden') and
        field.get_value('enabled')):
      return field
