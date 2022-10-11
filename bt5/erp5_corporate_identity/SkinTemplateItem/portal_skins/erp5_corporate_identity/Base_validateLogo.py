logo = context.REQUEST.get('field_your_override_logo_reference', '')
if not logo:
  return True

if logo.startswith('organisation_module') or logo.startswith('image_module'):
  try:
    if not context.restrictedTraverse(logo):
      return False
  except KeyError:
    return False

else:
  if not context.portal_catalog(portal_type=('Image', 'Web Illustration'), reference=logo):
    return False

return True
