"""
================================================================================
Display WebPage as slideshow if called with portal_skin=Slide parameter
================================================================================
"""
return context.WebPage_viewAsSlideshow(
  format=format,
  display_note=display_note,
  display_svg=display_svg,
  override_source_organisation_title=override_source_organisation_title,
  override_logo_reference=override_logo_reference,
  document_save=document_save,
  document_download=document_download,
  batch_mode=batch_mode,
  **kw
)
