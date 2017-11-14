"""
================================================================================
Export slideshow in any of the supported formats
================================================================================
"""
return context.WebPage_viewAsSlideshow(
  format=format,
  note_display=note_display,
  svg_display=svg_display,
  override_publisher_title=override_publisher_title,
  override_logo_reference=override_logo_reference,
  batch_mode=batch_mode,
  **kw
)
