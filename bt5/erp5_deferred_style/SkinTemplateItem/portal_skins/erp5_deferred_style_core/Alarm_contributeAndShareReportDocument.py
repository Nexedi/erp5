# type: (str, list[dict], str, str, str, str, str, DateTime.DateTime, Any)
portal = context.getPortalObject()

for attachment in attachment_list:
  document = portal.portal_contributions.newContent(
      data=attachment['content'],
      filename=attachment['name'],
      title=title,
      reference=reference,
      version=version,
      publication_section=publication_section,
      language=language,
      effective_date=effective_date,
  )
  document.share()
