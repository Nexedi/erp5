"""Prints all fields that are in 'not assigned' group.
This happens after updating a form where some fields have been added locally.
"""

for form_path, form in context.ZopeFind(
            context.portal_skins, obj_metatypes=['ERP5 Form'], search_sub=1):
  try:
    groups = form.get_groups()
  except AttributeError as e:
    print("%s is broken: %s" % (form_path, e))
  if 'not_assigned' in groups:
    print('Not assigned fields in %s: %s' % (form_path,
      [f.getId() for f in form.get_fields_in_group('not_assigned')]))

return printed
