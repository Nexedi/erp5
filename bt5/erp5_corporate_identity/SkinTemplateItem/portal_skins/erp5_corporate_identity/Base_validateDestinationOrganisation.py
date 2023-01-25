organisation = context.REQUEST.get('field_your_override_destination_organisation_title', '')

if not organisation:
  return True

if not context.portal_catalog(
  portal_type="Organisation",
  title= '="%s"' % organisation,
):
  return False

return True
