from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
getDocumentValue = context.getDocumentValue
error_list = []

# Check that the web section is more recent that the default pages.
if context.getAggregate():
  max_content_modification_date = context.getModificationDate()
  for default_page_reference in context.getAggregateReferenceList():
    if default_page_reference:
      for language in (None,) + context.getAvailableLanguageList():
        default_page = getDocumentValue(
            default_page_reference,
            language=language,
        )
        if default_page is not None:
          max_content_modification_date = max(
              default_page.getModificationDate(),
              max_content_modification_date,
          )
  if context.getModificationDate() < max_content_modification_date:
    error_list.append(
        "Web Section {} is older than default page".format(
            context.getRelativeUrl()))
    if fixit:
      portal.portal_workflow.doActionFor(
          context,
          'edit_action',
          comment=translateString('Edited Web Section, it was older than default page'))

return error_list
