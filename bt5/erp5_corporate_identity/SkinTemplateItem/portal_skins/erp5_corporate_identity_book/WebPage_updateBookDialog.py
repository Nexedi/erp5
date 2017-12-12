"""
================================================================================
Update a book dialog with parameters manually entered
================================================================================
"""
# XXX: url_param_string easily goes over 2000 chars and Base_callDialogMethod 
# sets an arbitrary limit for redirects at 2000 chars. Drop unnecessary fields,
# it's just a dialog update

from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  return context.Base_redirect(
    dialog_id,
    keep_items = dict(
      portal_status_message=translateString('Preview updated.'),
      cancel_url=cancel_url,
      portal_skin=portal_skin,
      format=format,
      display_svg=display_svg,
      document_save=document_save,
      document_download=document_download,
      override_document_description=override_document_description,
      override_document_short_title=override_document_short_title,
      override_document_title=override_document_title,
      override_document_version=override_document_version,
      override_logo_reference=override_logo_reference,
      override_source_person_title=override_source_person_title,
      override_document_reference=override_document_reference,
      override_source_organisation_title=override_source_organisation_title,
      transformation=transformation,
      include_content_table=include_content_table,
      include_history_table=include_history_table,
      include_reference_table=include_reference_table,
      include_linked_content=include_linked_content,
      include_report_content=include_report_content,
      #**kw
    )
  )
