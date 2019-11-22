software_release = context.SoftwarePublication_getRelatedSoftwareRelease()
software_release.SoftwareRelease_publishRelatedWebDocument()
message = context.getTitle() + " Published"
if hasattr(context, 'Base_redirect'):
  return context.Base_redirect(
    '',
    keep_items={
      'portal_status_message': context.Base_translateString(message),
    },
  )
