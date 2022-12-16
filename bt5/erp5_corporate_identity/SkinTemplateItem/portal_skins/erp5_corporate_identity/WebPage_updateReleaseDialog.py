"""
================================================================================
Update a press release dialog with parameters manually entered
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# display_svg:              display images as svg or png*
# display_about:            display automatic about (1)* or not (0)
# cancel_url:               url to go back from dialog
# dialog_id:                current dialog id
# portal_skin:              current skin used

# override_source_organisation_title: used instead of follow-up organisation
# override_source_person_title: used instead of contributor

# document_downalod:        download file directly
# document_save:            save file in document module

from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  request = container.REQUEST
  request.form['portal_status_message'] = translateString('Preview updated.')
  request.form['cancel_url'] = cancel_url
  request.form['portal_skin'] = portal_skin
  request.form['field_your_override_source_organisation_title'] = context.Base_getPressReleaseParameter(sender_company=True)
  request.form['field_your_override_source_person_title'] = context.Base_getPressReleaseParameter(sender=True)
  request.form['format'] = format
  request.form['display_svg'] = display_svg
  request.form['display_about'] = display_about
  request.form['document_save'] = document_save
  request.form['document_download'] = document_download
  return context.Base_renderForm(dialog_id)
