person = context.REQUEST.get('field_your_override_destination_person_title', '')

if not person:
  return True

if not context.portal_catalog(
  portal_type="Person",
  title= '="%s"' % person,
):
  return False

return True
