"""
================================================================================
Export WebPage as Press Release
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# display_svg:              display images as svg or png*
# display_about             display automatic about (*) or not
# batch_mode:               used for tests

# override_source_organisation_title: used instead of follow-up organisation
# override_source_person_title: used instead of contributor

# document_downalod:        download file directly
# document_save:            save file in document module

return context.WebPage_viewAsRelease(
  format=format,
  display_svg=display_svg,
  display_about=display_about,
  override_source_organisation_title=override_source_organisation_title,
  override_source_person_title=override_source_person_title,
  document_save=document_save,
  document_download=document_download,
  batch_mode=batch_mode,
  **kw
)
