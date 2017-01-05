portal = context.getPortalObject()

publication_section = portal.ERP5Site_getPreferredExpenseDocumentPublicationSectionValue()

proof_list = portal.portal_catalog(
  strict_follow_up_uid=context.getUid(),
  publication_section_uid=publication_section.getUid(),
  validation_state="shared",
  limit=1,
  select_list=["relative_url"]
  )

if not proof_list:
  return ""

return "/".join([portal.absolute_url(), proof_list[0].relative_url])
