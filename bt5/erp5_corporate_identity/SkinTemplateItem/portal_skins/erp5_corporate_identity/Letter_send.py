"""
================================================================================
Print letter in any of the supported formats
================================================================================
"""
new_skin_name = "Letter"
context.getPortalObject().portal_skins.changeSkin(new_skin_name)
if REQUEST is None:
  REQUEST = context.REQUEST
REQUEST.set('portal_skin', new_skin_name)

return context.Letter_viewAsLetter(
  format=format,
  display_head=display_head,
  display_svg=display_svg,
  display_source_address=display_source_address,
  override_source_organisation_title=override_source_organisation_title,
  override_source_person_title=override_source_person_title,
  override_destination_organisation_title=override_destination_organisation_title,
  override_destination_person_title=override_destination_person_title,
  override_date=override_date,
  document_save=document_save,
  document_download=document_download,
  batch_mode=batch_mode,
  **kw
)
