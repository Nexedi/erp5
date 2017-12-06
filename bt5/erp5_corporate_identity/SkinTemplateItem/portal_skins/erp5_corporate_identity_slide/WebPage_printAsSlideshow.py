"""
================================================================================
Print and download slideshow in PDF format
================================================================================
"""
return context.WebPage_viewAsSlideshow(
  format=format,
  display_note=display_note,
  display_svg=display_svg,
  override_source_organisation_title=override_source_organisation_title,
  override_logo_reference=override_logo_reference,
  batch_mode=batch_mode,
  document_download=document_download,
  document_save=document_save,
  **kw
)
