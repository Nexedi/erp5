if id is None:
  return "Failed. Missing image id."
if context.getPortalType() != "PDF":
  return "Failed. Not a pdf."

pdf_page = context
portal = pdf_page.getPortalObject()

system_preference = (
  portal.portal_preferences.getActiveSystemPreference()
)
preferred_document_conversion_server_url = (
  system_preference.getPreferredDocumentConversionServerUrl()
)
try:
  system_preference.edit(
    preferred_document_conversion_server_url="https://cloudooo.erp5.net/",
  )
  content_type, bmp_data = pdf_page.convert("bmp", frame=frame)
  image = portal.portal_catalog(
    portal_type="Image",
    id=id,
    limit=1
  )
  image[0].edit(data=bmp_data)
  return "Screenshot updated."
finally:
  system_preference.edit(
    preferred_document_conversion_server_url=preferred_document_conversion_server_url,
  )
