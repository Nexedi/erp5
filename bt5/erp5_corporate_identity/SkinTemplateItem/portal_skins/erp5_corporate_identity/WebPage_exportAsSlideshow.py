"""
================================================================================
Export slideshow in any of the supported formats
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# batch_mode:               used for tests

# override_source_organisation_title: to use instead of default company
# override_logo_reference:  to use instead of default company logo in footer

# document_download:        download file directly (default None)
# document_save:            save file in document module (default None)

# display_note:             display slide notes (1) or not (0)*
# display_svg:              display svg-images as svg or png*

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
