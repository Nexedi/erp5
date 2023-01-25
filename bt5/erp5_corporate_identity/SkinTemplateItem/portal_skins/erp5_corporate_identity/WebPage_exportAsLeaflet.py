"""
================================================================================
Export WebPage as Leaflet
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# display_side:             display side bar (1)* or not (0)
# display_svg:              display images as svg or png*
# batch_mode:               used for tests

# override_leaflet_header_title: custom title to use in the leaflet header
# override_source_organisation_title: used instead of follow-up organisation
# override_source_person_title: used instead of contributor

# document_downalod:        download file directly
# document_save:            save file in document module

return context.WebPage_viewAsLeaflet(
  format=format,
  display_side=display_side,
  display_svg=display_svg,
  override_leaflet_header_title=override_leaflet_header_title,
  override_source_organisation_title=override_source_organisation_title,
  override_source_person_title=override_source_person_title,
  override_logo_reference = override_logo_reference,
  document_save=document_save,
  document_download=document_download,
  batch_mode=batch_mode,
  **kw
)
