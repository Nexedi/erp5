"""
================================================================================
Export slideshow in any of the supported formats
================================================================================
"""
return context.WebPage_viewAsSlideshow(
  format=format,
  display_note=display_note,
  display_svg=display_svg,
  override_source_organisation_title=override_source_organisation_title,
  override_logo_reference=override_logo_reference,
  batch_mode=batch_mode,
  document_save=document_save,
  document_download=document_download,
  **kw
)
